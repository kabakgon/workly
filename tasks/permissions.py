from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAssigneeOrProjectOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        u = request.user
        if not u.is_authenticated:
            return False
        return (obj.assignee_id == u.id) or (obj.project and obj.project.owner_id == u.id) or u.is_staff or u.is_superuser
