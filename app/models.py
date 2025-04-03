from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class User(AbstractUser):
    pass  

class Restaurant(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Menu(models.Model):
    DAYS_OF_WEEK = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]

    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='menus')
    dish = models.CharField(max_length=255, default='none')
    day_of_week = models.CharField(max_length=3, choices=DAYS_OF_WEEK, default='mon')

    class Meta:
        unique_together = ("restaurant", "day_of_week")

    def __str__(self):
        return f"{self.dish} on {self.get_day_of_week_display()} ({self.restaurant.name})"

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'menu')  # Один користувач може проголосувати тільки один раз

    def __str__(self):
        return f"{self.user.username} → {self.menu}"
