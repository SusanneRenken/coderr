from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerProfile(BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'PATCH':
            return obj.user == user
        return False