from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsProjectOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        u = request.user
        return u.is_authenticated and (obj.owner_id == u.id or u.is_staff or u.is_superuser)
