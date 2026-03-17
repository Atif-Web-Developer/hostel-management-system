from django.db import models

class MySubscription(models.Model):
    # 1. User ka Email (Taake pehchan sakain kis ne paise diye)
    customer_email = models.EmailField(unique=True)
    
    # 2. Stripe ki Price ID (Jo aapne dashboard se nikali: price_1T6...)
    price_id = models.CharField(max_length=255)
    
    # 3. Subscription ka status (Active hai ya Expired?)
    status = models.CharField(max_length=50, default='Pending')
    
    # 4. Kab bani thi (Record ke liye)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_email} - {self.status}"