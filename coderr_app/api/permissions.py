"""Permission classes for coderr_app API.

These are small wrappers around the request user/profile state and
are used by the viewsets to gate access to specific actions (create,
update, destroy, etc.). No behavior changes are introduced here—only
explanatory docstrings were added.
"""

from rest_framework.permissions import BasePermission


class IsBusinessUser(BasePermission):
    """Allow access only to authenticated users with a business profile."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.type == 'business'


class IsCustomerUser(BasePermission):
    """Allow access only to authenticated users with a customer profile."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.type == 'customer'


class IsOfferOwner(BasePermission):
    """Object-level permission: only the offer owner may modify the offer."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOrderBusinessOwner(BasePermission):
    """Object-level permission: only the business user for an order may update it."""

    def has_object_permission(self, request, view, obj):
        return obj.business_user == request.user
    

class IsStaffUser(BasePermission):
    """Allow access only to staff users (used for delete operations)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class IsReviewAuthor(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.reviewer == request.user