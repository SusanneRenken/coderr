from rest_framework.permissions import BasePermission

class IsBusinessUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.type == 'business'

class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.type == 'customer'

class IsOfferOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsOrderBusinessOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.business_user == request.user
    
class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff

class IsReviewAuthor(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.reviewer == request.user