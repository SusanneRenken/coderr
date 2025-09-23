"""Admin bindings for auth_app models.

Registers Profile with a small ModelAdmin to ease inspection in Django
admin. This file only contains admin registration; it does not change model
behavior.
"""

from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	# Show key fields in the admin list view for quick scanning
	list_display = ("id", "user", "type", "created_at")
	# Allow searching by username/email and profile type
	search_fields = ("user__username", "user__email", "type")
	# Filter by profile type in the sidebar
	list_filter = ("type",)

