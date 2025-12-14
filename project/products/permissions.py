from rest_framework import permissions

# Only staff can create/update/delete
class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Safe methods: GET, HEAD, OPTIONS → anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Otherwise, only staff
        return request.user.is_authenticated and request.user.is_staff

# Only the owner or staff can see/modify order
class IsOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Staff can do anything
        if request.user.is_staff:
            return True
        # Otherwise only owner
        return obj.user == request.user
