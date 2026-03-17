from django.db import models
from django.contrib.auth.models import User   # 👈 THIS WAS MISSING


class SignUp(models.Model):
    full_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=40, unique=True, default='none@example.com')
    phone = models.CharField(max_length=11)
    cnic = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
