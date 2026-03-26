"""
URL configuration for First_Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from First_Project import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # auth
    path('', views.registration, name='registration'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('logout/', views.logout, name='logout'),
    path('forget_password/', views.forget_password, name='forget_password'),
    path('otp_verify/', views.otp_verify, name='otp_verify'),


    


    # dashboard
    path('index_file/', views.index_file, name='index_file'),
    

    # students
path('student/', views.student, name='student'),
path('student_view/', views.student_view, name='student_view'),


path('book_add/', views.book_add, name='book_add'),
path('add_book/', views.add_book, name='add_book'),
path('View_Book/', views.View_Book, name='View_Book'),
path('delete_book/', views.delete_book, name='delete_book'),
path('edit_data/', views.edit_data, name='edit_data'),
path('update_book/', views.update_book, name='update_book'),



path('add_room/', views.add_room, name='add_room'),
path('insert_room/', views.insert_room, name='insert_room'),
path('view_room/', views.view_room, name='view_room'),
path('toggle_room_status/', views.toggle_room_status, name='toggle_room_status'),
path('delete-room/', views.delete_room, name='delete-room'),
path('Active_room/', views.Active_room, name='Active_room'),
path('edit_data/', views.edit_data, name='edit_data'),
path('update_room/', views.update_room, name='update_room'),
path('room_allocation/', views.room_allocation, name='room_allocation'),
path('assign_room/', views.assign_room, name='assign_room'),
path('view_room_allocation/', views.view_room_allocation, name='view_room_allocation'),





path('add_staff/', views.add_staff, name='add_staff'),
path('view_staff/', views.view_staff, name='view_staff'),
path('insert_staff/', views.insert_staff, name='insert_staff'),
path('staff_delete/', views.staff_delete, name='staff_delete'),
path('staff_edit_view/', views.staff_edit_view, name='staff_edit_view'),
path('staff_update/', views.staff_update, name='staff_update'),




path('add_mess/', views.add_mess, name='add_mess'),
path('insert_mess/', views.insert_mess, name='insert_mess'),
path('view_mess/', views.view_mess, name='view_mess'),
path('view_custom_mess/', views.view_custom_mess, name='view_custom_mess'),



path('feepayment/', views.feepayment, name='feepayment'),
path('addfeepayment/', views.addfeepayment, name='addfeepayment'),
path('viewfeepayment/', views.viewfeepayment, name='viewfeepayment'),
path("checkout/<int:id>/", views.checkout_view, name="checkout"),



path('payment-success/', views.payment_success, name='payment_success'),
# path('payment-cancel/', views.payment_cancel, name='payment_cancel'),


path('pricing_page/', views.pricing_page, name='pricing_page'),
path('create_subscription/<str:price_id>/', views.create_subscription, name='create_subscription'),
path('subscription-success/', views.subscription_success, name='subscription-success'),
path('active_subscription/', views.active_subscription, name='active_subscription'),
path('all_active_subscription/', views.all_active_subscription, name='all_active_subscription'),



path('add_complaint/', views.add_complaint, name='add_complaint'),
path('insert_complaint/', views.insert_complaint, name='insert_complaint'),
path('my_complaints/', views.my_complaints, name='my_complaints'),







path('AddComplaintCategory/', views.AddComplaintCategory, name='AddComplaintCategory'),
path('ViewComplaintCategory/', views.ViewComplaintCategory, name='ViewComplaintCategory'),
path('insertComplaintCategory/', views.insertComplaintCategory, name='insertComplaintCategory'),
path('delete_category/', views.delete_category, name='delete_category'),
path('get_category_details/', views.get_category_details, name='get_category_details'),
path('update_category/', views.update_category, name='update_category'),





path('Scrapper/', views.Scrapper, name='Scrapper'),
path('scrape/', views.scrape, name='scrape'),









]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)