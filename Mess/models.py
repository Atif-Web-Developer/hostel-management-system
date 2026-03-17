from django.db import models

class MessMenu(models.Model):
    # Enums/Choices for Days
    DAY_CHOICES = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')
    ]
    
    # Enums/Choices for Meals
    MEAL_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner')
    ]

    # Pre-defined food items list
    FOOD_ITEMS_LIST = [
        ('Daal Chawal', 'Daal Chawal'),
        ('Chicken Karahi', 'Chicken Karahi'),
        ('Aloo Gobi', 'Aloo Gobi'),
        ('Biryani', 'Biryani'),
        ('Anda Paratha', 'Anda Paratha'),
        ('Omelette', 'Omelette'),
        ('Haleem', 'Haleem'),
        ('Custom', '--- Other (Write Custom) ---'),
    ]

    day = models.CharField(max_length=15, choices=DAY_CHOICES)
    meal_type = models.CharField(max_length=15, choices=MEAL_CHOICES)
    food_item = models.CharField(max_length=100, choices=FOOD_ITEMS_LIST)
    
    # Extra field for custom items
    custom_food_item = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="Only fill if 'Custom' is selected in food item"
    )
    
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)