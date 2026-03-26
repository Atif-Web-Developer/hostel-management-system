from django.db import models
from django.utils import timezone


class SignUp(models.Model):
    full_name  = models.CharField(max_length=30)
    email      = models.EmailField(max_length=40, unique=True, default='none@example.com')
    phone      = models.CharField(max_length=11)
    cnic       = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class PasswordResetOTP(models.Model):
    user       = models.ForeignKey(SignUp, on_delete=models.CASCADE)
    otp_code   = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_used    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.otp_code}"

    def is_expired(self):
        return timezone.now() > self.expires_at  # ← timezone.now() aware hai