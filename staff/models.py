from django.db import models

class Staff(models.Model):
    role_choices=[
        ('teacher','Teacher'),
        ('principal','Principal'),
        ('admin','Admin'),
        ('accountant','Accountant'),
        ('librarian', 'Librarian'),
        ('it', 'IT Support'),
        ('guard', 'Guard'),
        ('cleaner', 'Cleaner'),
    ]

    name=models.CharField(max_length=100)
    role=models.CharField(max_length=20,choices=role_choices)
    email=models.EmailField(unique=True,default='example@example.com')
    contact=models.CharField(max_length=15)
    picture=models.ImageField(upload_to='staff_pictures/',blank=True,null=True)
    def __str__(self):
        return self.name

    
# Create your models here.
