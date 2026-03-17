from django.db import models

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=30)
    roll_no = models.CharField(max_length=10, unique=True)
    student_class = models.CharField(max_length=30)
    email = models.EmailField(max_length=40, unique=True)
    contact = models.CharField(max_length=11)
    hostel_room = models.CharField(max_length=3)

    def __str__(self):
        return self.name