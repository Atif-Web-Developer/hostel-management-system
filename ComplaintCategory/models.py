from django.db import models


class ComplaintCategory(models.Model):

    PROFESSION_CHOICES = [
        ('Electrician', 'Electrician'),
        ('Plumber', 'Plumber'),
        ('Carpenter', 'Carpenter'),
        ('Mason', 'Mason (Mistry)'),
        ('Painter', 'Painter'),
        ('AC Technician', 'AC Technician'),
        ('Gardener', 'Gardener'),
        ('Cleaner', 'Janitor/Cleaner'),
        ('Welder', 'Welder'),
        ('IT Specialist', 'IT/Network Specialist'),
    ]

    name=models.CharField(max_length=100,unique=True)
    description=models.TextField(blank=True,null=True)
    profession = models.CharField(max_length=50, choices=PROFESSION_CHOICES, default='Other')
    email=models.EmailField(max_length=100,blank=True,null=True)
    picture=models.ImageField(upload_to='category_pics/',null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Complaint Categories" # Admin panel mein sahi naam dikhane ke liye
# Create your models here.
