from django.http import HttpResponse
from django.http import JsonResponse
import re
from django.urls import reverse
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.shortcuts import render
from authentication.models import SignUp
from authentication.models import PasswordResetOTP
from django.utils import timezone
from datetime import timedelta  
import random 


from students.models import Student
from library.models import Book
from hostel_management.models import Room
from hostel_management.models import RoomAllocation
from staff.models import Staff
from Mess.models import MessMenu
from FeePayment.models import FeePayment
from subscription.models import MySubscription
from complaint.models import Complaint
from ComplaintCategory.models import ComplaintCategory


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from playwright.sync_api import sync_playwright
import time


from django.shortcuts import render, get_object_or_404
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)  # <--- 'redirect' yahan hona chahiye
import requests
from django.conf import settings
import stripe
import os


def registration(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        cnic = request.POST.get("cnic", "").strip()

        if not all([name, email, phone, cnic]):
            return JsonResponse(
                {"status": "error", "message": "All fields are required"}
            )

        if SignUp.objects.filter(email=email).exists():
            return JsonResponse(
                {"status": "error", "message": "Email already registered"}
            )

        SignUp.objects.create(full_name=name, email=email, phone=phone, cnic=cnic)

        return JsonResponse(
            {
                "status": "success",
                "message": "Registered successfully",
                "redirect_url": reverse("sign_in"),
            }
        )

    # ✅ GET request
    return render(request, "registration.html")


def sign_in(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        cnic = request.POST.get("cnic", "").strip()

        if not email or not cnic:
            return JsonResponse(
                {"status": "error", "message": "All fields are required"}
            )

        # Pehle user ko dhoondo
        user = SignUp.objects.filter(email=email, cnic=cnic).first()

        if user:
            # Agar user mil jaye, tab session mein data dalo
            request.session["user_id"] = user.id
            request.session["user_full_name"] = user.full_name
            request.session["email"] = user.email

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Login successful",
                    "redirect_url": reverse("index_file"),
                }
            )
        else:
            # Agar user nahi mila
            return JsonResponse({"status": "error", "message": "Invalid email or CNIC"})

    return render(request, "sign_in.html")


def logout(request):

    request.session.flush()
    return redirect("sign_in")

def forget_password(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = SignUp.objects.get(email=email)
        except SignUp.DoesNotExist:
            return JsonResponse({
                'status' : 'error',
                'message': 'This email is not registered.'
            })

        otp_code = str(random.randint(100000, 999999))

        PasswordResetOTP.objects.filter(user=user).delete()

        PasswordResetOTP.objects.create(
            user       = user,
            otp_code   = otp_code,
            expires_at = timezone.now() + timedelta(minutes=10)
        )

        send_mail(
            subject        = 'Password Reset OTP',
            message        = f'Your OTP is: {otp_code}',
            from_email     = None,
            recipient_list = [email],
            fail_silently  = False,
        )

        # Session mein email save karo
        request.session['reset_email'] = email

        return JsonResponse({
            'status' : 'success',
            'message': 'OTP sent! Please check your email.'
        })

    return render(request, 'forget_password.html')




def otp_verify(request):
    if request.method == "POST":
        otp = request.POST.get('otp')

        if not otp:
            return JsonResponse({
                'status' : 'error',
                'message': 'OTP daalo'
            })

        try:
            # OTP database mein dhundo
            match_otp = PasswordResetOTP.objects.get(otp_code=otp)

        except PasswordResetOTP.DoesNotExist:
            return JsonResponse({
                'status' : 'error',
                'message': 'Galat OTP hai'
            })

        # Expire check karo
        if match_otp.is_expired():
            return JsonResponse({
                'status' : 'error',
                'message': 'OTP expire ho gaya, dobara bhejo'
            })

        # Pehle use hua check karo
        if match_otp.is_used:
            return JsonResponse({
                'status' : 'error',
                'message': 'OTP already use ho chuka hai'
            })

        # OTP sahi hai — mark as used
        match_otp.is_used = True
        match_otp.save()

        # Session mein save karo reset password ke liye
        request.session['otp_verified'] = True

        return JsonResponse({
            'status' : 'success',
            'message': 'OTP verified!'
        })

    return render(request, 'otp_verify.html')























def index_file(request):
    # Dono cheezein alag alag session se uthaein
    u_id = request.session.get("user_id")
    u_name = request.session.get("user_full_name")

    # Security Check: Agar login nahi hai to wapas login page pe bhej do
    if not u_id:
        return redirect("sign_in")

    total_student = Student.objects.count()
    total_Book = Book.objects.count()
    total_Room = Room.objects.count()
    total_Staff = Staff.objects.count()
    pending_fees_count = FeePayment.objects.filter(status="Pending").count()
    paid_fees_count = FeePayment.objects.filter(status="Paid").count()
    pending_complaints = Complaint.objects.filter(status="Pending").count()
    category_count = ComplaintCategory.objects.count()

    data = {
        "Student": total_student,
        "Book": total_Book,
        "Room": total_Room,
        "staff": total_Staff,
        "pending_fees": pending_fees_count,
        "paid_fees": paid_fees_count,
        "user_name": u_name,  # Template mein name show karne ke liye
        "user_id": u_id,  # Template mein ID use karne ke liye (agar zaroorat ho),
        "pending_complaints": pending_complaints,
        "category_count": category_count,
    }

    return render(request, "index.html", data)


# add student


def student(request):
    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        roll_no = request.POST.get("roll_no", "").strip()
        student_class = request.POST.get("student_class", "").strip()
        email = request.POST.get("email", "").strip()
        contact = request.POST.get("contact", "").strip()
        hostel_room = request.POST.get("hostel_room", "").strip()

        if not all([name, roll_no, student_class, email, contact, hostel_room]):
            return JsonResponse(
                {"status": "error", "message": "All fields are required"}
            )

        if Student.objects.filter(email=email).exists():
            return JsonResponse({"status": "error", "message": "Email already exists"})

        Student.objects.create(
            name=name,
            roll_no=roll_no,
            student_class=student_class,
            email=email,
            contact=contact,
            hostel_room=hostel_room,
        )

        return JsonResponse(
            {"status": "success", "message": "Student added successfully"}
        )

    # ✅ GET request (page show)
    return render(request, "students/students.html")


def student_view(request):
    students = Student.objects.all()
    return render(request, "students/viewstudents.html", {"student": students})


def book_add(request):
    students = Student.objects.all()
    return render(request, "library/book_add.html", {"students": students})


def add_book(request):
    if request.method == "POST":

        title = request.POST.get("title")
        author = request.POST.get("author")
        isbn = request.POST.get("isbn")
        issued_to_id = request.POST.get("issued_to")
        issue_date = request.POST.get("issue_date")
        return_date = request.POST.get("return_date")

        # Validation
        if not all([title, author, isbn, issued_to_id, issue_date, return_date]):
            return JsonResponse(
                {"status": "error", "message": "ALL Fields Are Required"}
            )

        # ForeignKey (ID → Object)
        try:
            issued_to = Student.objects.get(id=issued_to_id)
        except Student.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Invalid student selected"}
            )

        book = Book.objects.create(
            title=title,
            author=author,
            isbn=isbn,
            issued_to=issued_to,
            issue_date=issue_date,
            return_date=return_date,
        )

        return JsonResponse(
            {
                "status": "success",
                "message": "Book Added Successfully",
                "book_id": book.id,
            }
        )

    return JsonResponse({"error": "Invalid Request"})


def View_Book(request):
    books = Book.objects.all()  # ✅ Book model
    return render(request, "library/View_Book.html", {"books": books})


def delete_book(request):
    if request.method == "POST":
        book_id = request.POST.get("id")

        try:
            Book.objects.get(id=book_id).delete()
            return JsonResponse(
                {"status": "success", "message": "Book deleted successfully"}
            )
        except Book.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Book not found"})

    return JsonResponse({"error": "Invalid request"})


def edit_data(request):
    edit_data = request.GET.get("edit_id")
    try:
        book = Book.objects.get(id=edit_data)
        students = list(Student.objects.values("id", "name"))
        data = {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "issued_to": book.issued_to.name if book.issued_to else None,
            "issued_date": (
                book.issue_date.strftime("%Y-%m-%d") if book.issue_date else ""
            ),
            "return_date": (
                book.return_date.strftime("%Y-%m-%d") if book.return_date else ""
            ),
            "students": students,
        }
        return JsonResponse(data)
    except Book.DoesNotExist:
        return JsonResponse({"error": "Book Not Found"})


def update_book(request):
    if request.method == "POST":
        book_id = request.POST.get("book_id")
        title = request.POST.get("title")
        author = request.POST.get("author")
        isbn = request.POST.get("isbn")
        issued_to_id = request.POST.get("issued_to")
        issue_date = request.POST.get("issue_date")
        return_date = request.POST.get("return_date")
        try:
            book = Book.objects.get(id=book_id)
            book.title = title
            book.author = author
            book.isbn = isbn
            if issued_to_id:
                try:
                    issued_to_student = Student.objects.get(id=issued_to_id)
                    book.issued_to = issued_to_student
                except Student.DoesNotExist:
                    return JsonResponse(
                        {"status": "error", "message": "Student not found"}
                    )
            else:
                book.issued_to = None
            book.issue_date = issue_date
            book.return_date = return_date
            book.save()
            return JsonResponse(
                {"status": "success", "message": "Book updated successfully"}
            )
        except Book.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Book not found"})


def add_room(request):
    return render(request, "hostel_management/add_room.html")


def insert_room(request):
    if request.method == "POST":
        hostel_name = request.POST.get("hostel_name")
        room_number = request.POST.get("room_number")
        room_type = request.POST.get("room_type")
        capacity = int(request.POST.get("capacity"))  # Convert string to int
        floor = int(request.POST.get("floor"))  # Convert string to int
        is_active = request.POST.get("is_active", "True") == "True"  # string to boolean

        # Check only required string/int fields
        if not all([hostel_name, room_number, room_type, capacity, floor]):
            return JsonResponse(
                {"status": "error", "message": "All Fields Are Required"}
            )
        existing_rooom_count = Room.objects.filter(
            hostel_name=hostel_name,
            room_number=room_number,
            room_type=room_type,
            floor=floor,
        ).count()
        if existing_rooom_count >= capacity:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"Capacity Full! This Room in {hostel_name} hostel  on floor {floor} already has {capacity} people",
                }
            )
        Room.objects.create(
            hostel_name=hostel_name,
            room_number=room_number,
            room_type=room_type,
            capacity=capacity,
            floor=floor,
            is_active=is_active,
        )

        return JsonResponse({"status": "success", "message": "Room Added Successfully"})


def view_room(request):
    rooms = Room.objects.all()
    return render(request, "hostel_management/view_room.html", {"rooms": rooms})


def toggle_room_status(request):
    if request.method == "POST":
        room_id = request.POST.get("room_id")
        room = Room.objects.get(id=room_id)
        room.is_active = not room.is_active
        room.save()

        return JsonResponse({"status": "success", "new_status": room.is_active})


def delete_room(request):
    if request.method == "POST":
        delete_id = request.POST.get("delete_id")
        try:
            room_id = Room.objects.get(id=delete_id)
            room_id.delete()
            return JsonResponse({"status": 200, "message": "data deleted successfully"})
        except Room.DoesNotExist:
            return JsonResponse({"status": 404, "message": "Room not found"})
        except Exception as e:
            return JsonResponse({"status": 500, "message": str(e)})


def Active_room(request):
    try:
        active_rooms = Room.objects.filter(is_active=True)  # filter returns queryset
        return render(
            request, "hostel_management/Active_room.html", {"rooms": active_rooms}
        )
    except Exception as e:
        return JsonResponse({"status": 500, "message": str(e)})


def edit_data(request):
    if request.method == "POST":
        try:
            edit_id = request.POST.get("edit_id")
            room = Room.objects.get(id=edit_id)

            data = {
                "id": room.id,
                "hostel_name": room.hostel_name,
                "room_number": room.room_number,
                "room_type": room.room_type,
                "capacity": room.capacity,
                "floor": room.floor,
                "is_active": room.is_active,
            }

            return JsonResponse(
                {"status": 200, "message": "Data fetched successfully", "data": data}
            )

        except Room.DoesNotExist:
            return JsonResponse({"status": 404, "message": "Room not found"})
        except Exception as e:
            return JsonResponse({"status": 500, "message": str(e)})


def update_room(request):
    if request.method == "POST":
        # Fetch data from POST
        edit_room_id = request.POST.get("edit_room_id")
        edit_hostel_name = request.POST.get("edit_hostel_name")
        edit_room_number = request.POST.get("edit_room_number")
        edit_room_type = request.POST.get("edit_room_type")
        edit_capacity = request.POST.get("edit_capacity")
        edit_floor = request.POST.get("edit_floor")
        edit_is_active = (
            request.POST.get("edit_is_active") == "True"
        )  # convert string to boolean

        # Validation: check required fields
        if not all(
            [
                edit_room_id,
                edit_hostel_name,
                edit_room_number,
                edit_room_type,
                edit_capacity,
                edit_floor,
            ]
        ):
            return JsonResponse(
                {"status": "error", "message": "All Fields Are Required"}
            )

        try:
            # Get the room instance
            room = Room.objects.get(id=edit_room_id)

            # Update fields
            room.hostel_name = edit_hostel_name
            room.room_number = edit_room_number
            room.room_type = edit_room_type
            room.capacity = edit_capacity
            room.floor = edit_floor
            room.is_active = edit_is_active

            # Save to DB
            room.save()

            return JsonResponse(
                {"status": "success", "message": "Room Updated Successfully"}
            )
        except Room.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Room Not Found"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})


def room_allocation(request):
    students = Student.objects.all()
    rooms = Room.objects.filter(is_active=True)

    allocations = RoomAllocation.objects.select_related("student", "room")

    return render(
        request,
        "hostel_management/room_allocation.html",
        {"students": students, "rooms": rooms, "allocations": allocations},
    )


def assign_room(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        room_id = request.POST.get("room_id")

        # Check if fields exist
        if not all([student_id, room_id]):
            return JsonResponse(
                {"status": "error", "message": "Student and Room are required"}
            )

        try:
            student = Student.objects.get(id=student_id)
            room = Room.objects.get(id=room_id)

            # 1️⃣ Check if student is already assigned to this room
            existing_allocation = RoomAllocation.objects.filter(
                student=student, room=room
            ).exists()
            if existing_allocation:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": f"{student.name} is already assigned to this room!",
                    }
                )
            already_assigned = RoomAllocation.objects.filter(student=student).exists()
            if already_assigned:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": f"{student.name} is already assigned to a room",
                    }
                )

            # 2️⃣ Check room capacity
            allocated_count = RoomAllocation.objects.filter(room=room).count()
            if allocated_count >= room.capacity:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": f"Room {room.room_number} in {room.hostel_name} is already full!",
                    }
                )

            # 3️⃣ Create allocation
            RoomAllocation.objects.create(student=student, room=room)

            return JsonResponse(
                {
                    "status": "success",
                    "message": f"{student.name} has been assigned to room {room.room_number} successfully!",
                }
            )

        except Student.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Student not found"})
        except Room.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Room not found"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return HttpResponse("request")


def view_room_allocation(request):
    allocations = RoomAllocation.objects.select_related("student", "room")
    return render(
        request,
        "hostel_management/view_room_allocation.html",
        {"allocations": allocations},
    )


def add_staff(request):
    return render(request, "staff/add_staff.html")


def insert_staff(request):
    if request.method == "POST":

        name = request.POST.get("name")
        role = request.POST.get("role")
        email = request.POST.get("email")
        contact = request.POST.get("contact")
        picture = request.FILES.get("picture")

        # 🔹 Required fields validation (picture optional)
        if not all([name, role, email, contact]):
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Name, Role, Email and Contact are required",
                }
            )

        # 🔹 Email unique validation
        if Staff.objects.filter(email=email).exists():
            return JsonResponse({"status": "error", "message": "Email already exists"})

        # 🔹 Save data
        staff = Staff.objects.create(
            name=name, role=role, email=email, contact=contact, picture=picture
        )

        return JsonResponse(
            {
                "status": "success",
                "message": "Staff added successfully",
                "staff_id": staff.id,
                "name": staff.name,
            }
        )

    # 🔹 If method is not POST
    return JsonResponse({"status": "error", "message": "Invalid request method"})


def view_staff(request):
    get_data = Staff.objects.all()
    return render(request, "staff/view_staff.html", {"data": get_data})


def staff_delete(request):
    staff_id = request.GET.get("id")

    try:
        get_data = Staff.objects.get(id=staff_id)

        # 1. Image file check karein aur delete karein
        if get_data.picture:
            file_path = get_data.picture.path
            # Check karein ke file folder mein mojood hai ya nahi
            if os.path.exists(file_path):
                # os.remove() ke andar path dena zaroori hai
                os.remove(file_path)

        # 2. Database record delete karein
        get_data.delete()

        return JsonResponse(
            {
                "status": "success",
                "message": "Staff member and image deleted successfully",
            }
        )

    except Staff.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "The ID does not exist"}, status=404
        )


def staff_edit_view(request):
    staff_id = request.GET.get("id")
    staff = Staff.objects.get(id=staff_id)
    data = {
        "id": staff.id,
        "name": staff.name,
        "email": staff.email,
        "role": staff.role,
        "contact": staff.contact,
        "picture": staff.picture.url,
    }
    return JsonResponse(data)


def staff_update(request):
    if request.method == "POST":
        staff_id = request.POST.get("staff_id")
        try:
            get_staff = Staff.objects.get(id=staff_id)
            get_staff.name = request.POST.get("name")
            get_staff.email = request.POST.get("email")
            get_staff.role = request.POST.get("role")
            get_staff.contact = request.POST.get("contact")
            if "picture" in request.FILES:
                get_staff.picture = request.FILES["picture"]
            else:
                pass
            get_staff.save()
            return JsonResponse(
                {"status": "success", "message": "staff updated successfully"}
            )
        except staff.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Staff not found!"})
    return JsonResponse({"status": "error", "message": "Invalid request"})


def add_mess(request):
    return render(request, "mess/add_mess.html")


def insert_mess(request):
    if request.method == "POST":
        day = request.POST.get("day")
        meal_type = request.POST.get("meal_type")
        food_item = request.POST.get("food_item")
        custom_food_item = request.POST.get("custom_food_item")
        price = request.POST.get("price")

        try:
            # 1. Database mein save karein
            obj = MessMenu.objects.create(
                day=day,
                meal_type=meal_type,
                food_item=food_item,
                custom_food_item=custom_food_item,
                price=price,
            )

            # 2. Agar "Custom" hai to Emails bhejein
            if food_item == "Custom":
                # List nikalna lazmi hai
                get_students = list(Student.objects.values_list("email", flat=True))

                if get_students:
                    subject = f"📢 Special {meal_type} Alert!"
                    message = f"Assalam-o-Alaikum!\n\nToday's special {meal_type} is {custom_food_item}.\nPrice: Rs.{price}\n\nDon't miss it!"
                    from_email = (
                        "rehmanatif682@gmail.com"  # Apni sahi Gmail yahan likhein
                    )

                    # send_mail function
                    send_mail(
                        subject,
                        message,
                        from_email,
                        get_students,  # Ye aapki list hai students ki
                        fail_silently=False,
                    )
                    return JsonResponse(
                        {
                            "status": "success",
                            "message": "Menu saved successfully and email sent!",
                        }
                    )

            return JsonResponse(
                {"status": "success", "message": "Menu saved successfully!"}
            )

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request"})


def view_mess(request):
    get_data = MessMenu.objects.exclude(food_item="Custom").order_by("id")
    return render(request, "mess/view_mess.html", {"data": get_data})


def view_custom_mess(request):
    # 'all()' ko hata kar '.filter()' lagayein taake sirf Custom data aaye
    get_data = MessMenu.objects.filter(food_item="Custom").order_by("id")
    return render(request, "mess/view_custom_mess.html", {"data": get_data})


def feepayment(request):
    student = Student.objects.all()

    return render(request, "feepayment/addfeepayment.html", {"students": student})


def addfeepayment(request):
    if request.method == "POST":
        student_id = request.POST.get("student")
        amount = request.POST.get("amount")

        # Convert amount to integer
        try:
            amount = int(amount)
        except:
            return JsonResponse({"status": "error", "message": "Invalid amount"})

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Student not found"})

        # FeePayment create
        FeePayment.objects.create(student=student, amount=amount, status="Pending")

        return JsonResponse(
            {
                "status": "success",
                "message": "Fee added successfully. Status is Pending",
            }
        )

    # If request method is not POST
    return JsonResponse({"status": "error", "message": "Invalid request"})


def viewfeepayment(request):
    get_data = FeePayment.objects.all()
    return render(request, "feepayment/viewfeepayment.html", {"data": get_data})


stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout_view(request, id):
    payment = get_object_or_404(FeePayment, id=id)

    # Terminal mein check karne ke liye
    print(f"DEBUG: Request method is {request.method}")

    if request.method == "POST":
        print("DEBUG: POST trigger ho gaya!")
        try:
            stripe_amount = int(payment.amount * 100)

            # Create Stripe Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "pkr",
                            "product_data": {
                                # Student ka name yahan product_data ke andar aayega
                                "name": f"Hostel Fee - {payment.student.name} (ID: {payment.id})",
                            },
                            "unit_amount": stripe_amount,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                # Success aur Cancel URLs
                success_url=f"http://127.0.0.1:8000/payment-success/?session_id={{CHECKOUT_SESSION_ID}}&payment_id={payment.id}",
                cancel_url="http://127.0.0.1:8000/payment-cancel/",
            )

            print(f"DEBUG: Redirecting to {checkout_session.url}")
            return redirect(checkout_session.url, code=303)

        except Exception as e:
            print(f"DEBUG STRIPE ERROR: {e}")
            return HttpResponse(f"Error: {e}")

    return render(request, "checkout.html", {"payment": payment})


def payment_success(request):
    payment_id = request.GET.get("payment_id")
    payment = get_object_or_404(FeePayment, id=payment_id)
    # Status update
    payment.status = "Paid"
    payment.save()
    return render(request, "payment_success.html", {"payment": payment})


def pricing_page(request):
    return render(request, "subscription/pricing.html")


def create_subscription(request, price_id):
    user_email = request.session.get("email")
    if not user_email:
        return redirect("sign_in/")  # Wapas login par bhej dein
    try:

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer_email=user_email,  # Stripe ko user ka email dena zaroori hai
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            # Yahan humne {CHECKOUT_SESSION_ID} bhejni hai taake Stripe wapas ID bheje
            success_url="http://127.0.0.1:8000/subscription-success/?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://127.0.0.1:8000/pricing_page/",
        )

        # *** YAHAN DATA SAVE HOGA ***
        # Stripe par bhejne se pehle record database mein 'Pending' status se save karein
        MySubscription.objects.update_or_create(
            customer_email=user_email,
            defaults={"price_id": price_id, "status": "Pending"},
        )

        return redirect(checkout_session.url, code=303)

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")


def subscription_success(request):
    session_id = request.GET.get("session_id")
    user_email = request.session.get("email")  # Session se email liya

    if session_id and user_email:
        # Stripe se confirm kiya
        session = stripe.checkout.Session.retrieve(session_id)
        stripe_email = session.customer_details.email

        # Agar session wala email aur stripe wala email match kar jayein
        if stripe_email == user_email:
            sub = MySubscription.objects.get(customer_email=user_email)
            sub.status = "Active"
            sub.save()

            return render(
                request,
                "subscription/subscription_success.html",
                {"email": user_email, "status": "Active"},
            )

    return HttpResponse("Payment verification failed!")


def active_subscription(request):
    user_email = request.session.get("email")
    if not user_email:
        return redirect("sign_in/")
    active_plans = MySubscription.objects.filter(
        customer_email=user_email, status="Active"
    ).order_by("-created_at")
    context = {
        "active_plans": active_plans,
        "user_full_name": request.session.get("user_full_name"),
    }
    return render(request, "subscription/active_subscription.html", context)


def all_active_subscription(request):
    user_email = request.session.get("email")
    if not user_email:
        return redirect("sign_in/")
    active_plans = MySubscription.objects.filter(status="Active").order_by(
        "-created_at"
    )
    context = {
        "active_plans": active_plans,
        "user_full_name": request.session.get("user_full_name"),
    }
    return render(request, "subscription/All_active_subscriptions.html", context)


def AddComplaintCategory(request):
    return render(request, "ComplaintCategory/AddComplaintCategory.html")


def insertComplaintCategory(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        description = request.POST.get("description")
        profession = request.POST.get("profession")
        picture = request.FILES.get("picture")

        # 1. Validation Checks
        if not name:
            return JsonResponse(
                {"status": "error", "message": "Please fill Category Name"}
            )
        if not email:
            return JsonResponse(
                {"status": "error", "message": "Please fill Technician Email"}
            )
        if not description:
            return JsonResponse(
                {"status": "error", "message": "Please fill Description"}
            )
        if not picture:
            return JsonResponse(
                {"status": "error", "message": "Please upload a Picture"}
            )
        if not profession:
            return JsonResponse(
                {"status": "error", "message": "Please fill a profession"}
            )

        try:
            # 2. Database mein Entry
            # Yaad rakhein: left side model field hai, right side aapka variable
            new_cat = ComplaintCategory.objects.create(
                name=name,
                email=email,
                description=description,
                profession=profession,
                picture=picture,
            )
            return JsonResponse(
                {
                    "status": "success",
                    "message": "ComplaintCategory Added Successfully!",
                }
            )

        except Exception as e:
            # Agar koi error aaye (maslan image size barha ho ya name duplicate ho)
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse(
        {"status": "error", "message": "Invalid Request Method"}, status=400
    )


def ViewComplaintCategory(request):
    get_data = ComplaintCategory.objects.all().order_by("-id")
    return render(
        request, "ComplaintCategory/ViewComplaintCategory.html", {"data": get_data}
    )


def delete_category(request):
    if request.method == "POST":
        category_id = request.POST.get("id")
        try:
            category = ComplaintCategory.objects.get(id=category_id)

            # 3. Pehle check karein ke kya image mojood hai?
            if category.picture:
                image_path = (
                    category.picture.path
                )  # Ye server par file ka poora rasta batata hai

                # 4. Check karein ke file asliyat mein folder mein hai ya nahi
                if os.path.exists(image_path):
                    os.remove(image_path)  # File ko folder se delete kar do

            # 5. Ab database se record delete karein
            category.delete()

            return JsonResponse(
                {"status": "success", "message": "Category and its Image deleted!"}
            )

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request."})


def get_category_details(request):
    if request.method == "GET":
        cat_id = request.GET.get("id")
        try:
            # Database se data uthaya
            cat = ComplaintCategory.objects.get(id=cat_id)

            return JsonResponse(
                {
                    "status": "success",
                    "name": cat.name,
                    "profession": cat.profession,
                    "email": cat.email,
                    "description": cat.description,
                    "id": cat.id,
                    "picture": cat.picture.url if cat.picture else None,
                }
            )
        except ComplaintCategory.DoesNotExist:  # Brackets hata diye yahan se
            return JsonResponse({"status": "error", "message": "Category not found"})

    return JsonResponse({"status": "error", "message": "Invalid request"})


def update_category(request):
    if request.method == "POST":
        cat_id = request.POST.get("edit_id")

        try:
            # 1. Database se purana record nikalo
            category = ComplaintCategory.objects.get(id=cat_id)

            # 2. Saari Text Fields update karo (Jo user ne modal mein change ki hain)
            category.name = request.POST.get("edit_name")
            category.profession = request.POST.get("edit_profession")
            category.email = request.POST.get("edit_email")
            category.description = request.POST.get("edit_description")

            if "edit_picture" in request.FILES:
                # Purani picture delete karne ka logic
                if category.picture:
                    if os.path.exists(category.picture.path):
                        os.remove(category.picture.path)

                # Nayi picture set karo
                category.picture = request.FILES.get("edit_picture")

            # 4. FINAL SAVE (Ye saari fields ko aik sath DB mein update kar dega)
            category.save()

            return JsonResponse(
                {"status": "success", "message": "Sura data update ho gaya hai!"}
            )

        except ComplaintCategory.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Category nahi mili!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid Request"})


def add_complaint(request):
    students = Student.objects.all()
    rooms = Room.objects.all()  # Variable name 'rooms' hai
    complaint_category = ComplaintCategory.objects.all()

    return render(
        request,
        "complaint/add_complaint.html",
        {
            "students": students,
            "rooms": rooms,  # Yahan 'room' nahi balkay 'rooms' hona chahiye
            "complaint_category": complaint_category,
        },
    )


def insert_complaint(request):
    if request.method == "POST":
        student_id = request.POST.get("student")
        room_id = request.POST.get("room_no")
        category_id = request.POST.get("category")
        description = request.POST.get("description")
        status = request.POST.get("status", "Pending")
        complaint_img = request.FILES.get("complaint_img")

        # 1. Validation Checks
        if not student_id:
            return JsonResponse(
                {"status": "error", "message": "Please select a Student"}
            )
        if not room_id:
            return JsonResponse({"status": "error", "message": "Please select a Room"})
        if not category_id:
            return JsonResponse(
                {"status": "error", "message": "Please select a Category"}
            )
        if not description:
            return JsonResponse(
                {"status": "error", "message": "Please write some Description"}
            )
        if not complaint_img:
            return JsonResponse(
                {"status": "error", "message": "Please upload a Complaint Image"}
            )

        try:
            # 2. Objects get karna
            student_obj = Student.objects.get(id=student_id)
            room_obj = Room.objects.get(id=room_id)
            category_obj = ComplaintCategory.objects.get(id=category_id)

            # 3. Database mein Entry
            Complaint.objects.create(
                student=student_obj,
                room_no=room_obj,
                category=category_obj,
                description=description,
                status=status,
                complaint_img=complaint_img,
            )

            # 4. Email bhejne ka logic
            technician_email = category_obj.email
            if technician_email:
                subject = f"🚨 New {category_obj.name} Complaint - Room {room_obj.room_number}"
                message = f"Assalam-o-Alaikum,\n\nAik nayi complaint ayi hai.\n\nStudent: {student_obj.name}\nMasla: {description}\nStatus: Pending\n\nMeharbani farma kar isay check karein."

                try:
                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [technician_email],
                        fail_silently=False,
                    )
                except Exception as mail_err:
                    # Email fail ho to sirf terminal pe dikhaye, user ko error na de
                    print(f"Email Sending Error: {mail_err}")

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Complaint Registered and Email Sent!",
                    "email of technician is": technician_email,
                }
            )

        except Student.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Student not found!"})
        except Room.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Room not found!"})
        except ComplaintCategory.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Category not found!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return HttpResponse("Invalid Request")


def my_complaints(request):
    get_record = Complaint.objects.select_related(
        "room_no", "student", "category"
    ).all()
    return render(request, "complaint/my_complaints.html", {"data": get_record})


def Scrapper(request):
    return render(request, "Scrapper/Scrapper.html")

def scrape(request):

    if request.method == "GET":

        platform = request.GET.get("platform")
        link = request.GET.get("link")

        if platform == "facebook":

            products = []

            with sync_playwright() as p:

                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(link)
                time.sleep(5)

                images = page.query_selector_all("img")

                count = 0

                for img in images:

                    src = img.get_attribute("src")

                    if src and "scontent" in src:

                        description = ""
                        price = ""

                        try:
                            parent = img.evaluate(
                                "el => el.closest('div[role=\"article\"]')?.innerText"
                            )

                            if parent:
                                lines = parent.strip().split("\n")
                                description = lines[0] if lines else ""

                                for line in lines:
                                    if any(
                                        x in line for x in ["Rs", "PKR", "$", "£", "/-"]
                                    ):
                                        price = line.strip()
                                        break

                        except:
                            description = "No description"
                            price = "N/A"

                        products.append({
                            "title": "Facebook Product",
                            "price": price if price else "N/A",
                            "image": src,
                            "description": description if description else "No description",
                        })

                        count += 1

                    if count == 8:
                        break

                browser.close()

            return JsonResponse(products, safe=False)

        elif platform == "instagram":

            products = []

            with sync_playwright() as p:

                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto("https://www.instagram.com/accounts/login/")
                time.sleep(5)

                page.fill("input[name='username']", "thebagempire.official")
                page.fill("input[name='password']", "Developer_bags_@9795")
                page.click("button[type='submit']")
                time.sleep(8)

                page.goto(link)
                time.sleep(5)

                posts = page.query_selector_all("article img")

                count = 0

                for img in posts:

                    src = img.get_attribute("src")

                    if src and "http" in src:

                        description = img.get_attribute("alt")

                        products.append({
                            "title": "Instagram Product",
                            "price": "N/A",
                            "image": src,
                            "description": description if description else "No description",
                        })

                        count += 1

                    if count == 8:
                        break

                browser.close()

            return JsonResponse(products, safe=False)