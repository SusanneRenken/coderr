from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default='customer')
