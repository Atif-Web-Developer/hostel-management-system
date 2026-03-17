from django.db import models
from students.models import Student

class Room(models.Model):

    HOSTEL_CHOICES = (
        ('boys', 'Boys Hostel'),
        ('girls', 'Girls Hostel'),
    )

    ROOM_TYPE_CHOICES = (
        ('single', 'Single'),
        ('double', 'Double'),
        ('triple', 'Triple'),
    )

    hostel_name = models.CharField(
        max_length=20,
        choices=HOSTEL_CHOICES
    )

    room_number = models.CharField(
        max_length=10,
            )

    room_type = models.CharField(
        max_length=10,
        choices=ROOM_TYPE_CHOICES
    )

    capacity = models.PositiveIntegerField()

    floor = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room_number} - {self.hostel_name}"

class RoomAllocation(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    room=models.ForeignKey(Room,on_delete=models.CASCADE)
    assigned_date=models.DateField(auto_now_add=True)

    class Meta:
        unique_together=('student','room')