from django.db import models
from students.models import Student
import uuid


class FeePayment(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    amount = models.IntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    reference_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    safepay_order_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.student} - {self.amount} - {self.status}"