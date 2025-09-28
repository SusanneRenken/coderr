"""auth_app.models

Profile model for storing lightweight user profile data that extends the
Django User model via a OneToOne relation. This module intentionally keeps
the model small: it stores profile metadata (type), an optional uploaded
file, contact fields and a creation timestamp.

No business logic lives in this model; it's primarily a data container used
by the API serializers and views in `auth_app.api`.
"""

from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """A simple profile attached to Django's User.

    Fields:
    - user: OneToOne link to Django's User model (accessible as user.profile)
    - type: 'customer' or 'business' (used for permission checks elsewhere)
    - file/uploaded_at: optional uploaded file and its timestamp
    - location, tel, description, working_hours: optional contact/meta fields
    - created_at: automatic creation timestamp
    """

    TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]

    # Link to the Django User; related_name='profile' allows user.profile
    # Make the Profile primary key identical to the User primary key so that
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True,
    )

    # Business vs customer is used in views/permissions to control behavior
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='customer')

    # Optional uploaded profile file (stored under MEDIA_ROOT/profile/)
    file = models.FileField(upload_to='profile/', blank=True, null=True)
    uploaded_at = models.DateTimeField(blank=True, null=True)

    # Optional contact and descriptive fields
    location = models.CharField(max_length=100, blank=True, null=True)
    tel = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    working_hours = models.CharField(max_length=50, blank=True, null=True)

    # Record creation time
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Useful representation for admin and debugging
        return f"Profile of {self.user.username}"
