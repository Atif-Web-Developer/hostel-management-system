from django.db import models
from students.models import Student
from hostel_management.models import Room
# Apne naye model ko import karein
from ComplaintCategory.models import ComplaintCategory 

class Complaint(models.Model): 
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In-Progress', 'In-Progress'),
        ('Resolved', 'Resolved'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room_no = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    # --- MODIFICATION: Ab category dynamic hogi ---
    category = models.ForeignKey(ComplaintCategory, on_delete=models.SET_NULL, null=True)
    
    description = models.TextField()
    complaint_img = models.ImageField(upload_to='complaint_pics/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # --- MODIFICATION: Dono dates track karein ---
    created_at = models.DateTimeField(auto_now_add=True) # Time bhi track hoga
    updated_at = models.DateTimeField(auto_now=True)     # Jab bhi status badle ga, ye update hogi

    def __str__(self):
        # self.category.name use karein kyunke ab ye aik object hai
        return f"{self.category.name if self.category else 'No Category'} - Room {self.room_no} ({self.status})"