from django.contrib import admin
from .models import Offer, OfferDetail, Order, Review


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "user", "created_at", "updated_at")
	search_fields = ("title", "description", "user__username")
	list_filter = ("created_at",)


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
	list_display = ("id", "offer", "offer_type", "price", "delivery_time_in_days")
	search_fields = ("offer__title", "offer__user__username")
	list_filter = ("offer_type",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ("id", "offer_detail", "customer_user", "business_user", "status", "created_at")
	search_fields = ("offer_detail__title", "customer_user__username", "business_user__username")
	list_filter = ("status",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = ("id", "business_user", "reviewer", "rating", "created_at")
	search_fields = ("business_user__username", "reviewer__username", "description")
	list_filter = ("rating",)

