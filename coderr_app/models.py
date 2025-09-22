from django.db import models
from django.contrib.auth.models import User


class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.FileField(upload_to='offers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]

    offer = models.ForeignKey(
        Offer, related_name='details', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.IntegerField()
    features = models.JSONField(default=list)
    offer_type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default='basic')

    def __str__(self):
        return f"Detail for {self.offer.title}"
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="business_orders")
    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id}: {self.offer_detail.title} ({self.status})"

class Review(models.Model):
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_reviews")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_reviews")
    rating = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review {self.id} for {self.business_user.username} by {self.reviewer.username}"
