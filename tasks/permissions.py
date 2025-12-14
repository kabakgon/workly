from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAssigneeOrProjectOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Allow all authenticated users to view and create tasks
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        u = request.user
        if not u.is_authenticated:
            return False
        return (obj.assignee_id == u.id) or (obj.project and obj.project.owner_id == u.id) or u.is_staff or u.is_superuser


class IsDependencyProjectOwnerOrReadOnly(BasePermission):
    """
    Permission class for Dependency objects.
    Checks if user is owner of the project that contains the tasks in the dependency.
    """
    def has_permission(self, request, view):
        # Allow all authenticated users to view list
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        u = request.user
        if not u.is_authenticated:
            return False
        
        # Check if user is staff or superuser
        if u.is_staff or u.is_superuser:
            return True
        
        # Check if user is owner of the project containing the predecessor or successor task
        # Both tasks should be in the same project, so we check either one
        if hasattr(obj, 'predecessor') and obj.predecessor:
            project = obj.predecessor.project
            if project and project.owner_id == u.id:
                return True
        
        if hasattr(obj, 'successor') and obj.successor:
            project = obj.successor.project
            if project and project.owner_id == u.id:
                return True
        
        return False
