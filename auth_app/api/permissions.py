"""Permission classes used by auth_app.api.

IsOwnerProfile allows safe methods for
any authenticated user and restricts PATCH to the profile owner.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerProfile(BasePermission):
    """Allow safe methods for everyone; only owner may PATCH their profile."""

    def has_permission(self, request, view):
        # Ensure the user is authenticated for non-public profile actions
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'PATCH':
            # Only the owner of the profile may PATCH it
            return obj.user == user
        return False