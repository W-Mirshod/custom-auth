from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from .models import UserRole, AccessRoleRule, BusinessElement


class HasElementPermission(permissions.BasePermission):
    """
    Custom permission class to check if user has permission for a business element.
    
    Usage:
        permission_classes = [HasElementPermission]
        permission_element = 'products'  # Name of business element
        permission_action = 'read'  # Action: read, read_all, create, update, update_all, delete, delete_all
    """
    
    def has_permission(self, request, view):
        """Check if user has permission for the requested action"""
        from django.contrib.auth.models import AnonymousUser
        # Check if user is authenticated
        if not request.user or isinstance(request.user, AnonymousUser) or not hasattr(request.user, 'id'):
            raise AuthenticationFailed('Authentication required')
        
        # Get element name from view
        element_name = getattr(view, 'permission_element', None)
        if not element_name:
            # Try to get from action or default
            element_name = getattr(view, 'permission_element_name', None)
        
        # Get action from view
        action = getattr(view, 'permission_action', None)
        if not action:
            # Map HTTP methods to actions
            if request.method == 'GET':
                action = 'read'
            elif request.method == 'POST':
                action = 'create'
            elif request.method in ['PUT', 'PATCH']:
                action = 'update'
            elif request.method == 'DELETE':
                action = 'delete'
        
        # Get user's roles
        user_roles = UserRole.objects.filter(user=request.user).select_related('role')
        
        # Get business element
        try:
            element = BusinessElement.objects.get(name=element_name)
        except BusinessElement.DoesNotExist:
            raise PermissionDenied(f'Business element "{element_name}" not found')
        
        # Check permissions for each role
        for user_role in user_roles:
            try:
                rule = AccessRoleRule.objects.get(role=user_role.role, element=element)
                
                # Check specific permission based on action
                if action == 'read':
                    if rule.read_permission or rule.read_all_permission:
                        return True
                elif action == 'read_all':
                    if rule.read_all_permission:
                        return True
                elif action == 'create':
                    if rule.create_permission:
                        return True
                elif action == 'update':
                    if rule.update_permission or rule.update_all_permission:
                        return True
                elif action == 'update_all':
                    if rule.update_all_permission:
                        return True
                elif action == 'delete':
                    if rule.delete_permission or rule.delete_all_permission:
                        return True
                elif action == 'delete_all':
                    if rule.delete_all_permission:
                        return True
            except AccessRoleRule.DoesNotExist:
                continue
        
        # No permission found
        raise PermissionDenied(f'Permission denied for action "{action}" on "{element_name}"')
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission for a specific object"""
        # First check general permission
        if not self.has_permission(request, view):
            return False
        
        # Get action
        action = getattr(view, 'permission_action', None)
        if not action:
            if request.method == 'GET':
                action = 'read'
            elif request.method in ['PUT', 'PATCH']:
                action = 'update'
            elif request.method == 'DELETE':
                action = 'delete'
        
        # Check if user owns the object (for non-_all permissions)
        if hasattr(obj, 'owner_id'):
            is_owner = obj.owner_id == request.user.id
            
            # For read/update/delete, check if user owns the object or has _all permission
            if action in ['read', 'update', 'delete']:
                element_name = getattr(view, 'permission_element', None)
                if element_name:
                    user_roles = UserRole.objects.filter(user=request.user).select_related('role')
                    try:
                        element = BusinessElement.objects.get(name=element_name)
                        for user_role in user_roles:
                            try:
                                rule = AccessRoleRule.objects.get(role=user_role.role, element=element)
                                
                                if action == 'read':
                                    if rule.read_all_permission or (rule.read_permission and is_owner):
                                        return True
                                elif action == 'update':
                                    if rule.update_all_permission or (rule.update_permission and is_owner):
                                        return True
                                elif action == 'delete':
                                    if rule.delete_all_permission or (rule.delete_permission and is_owner):
                                        return True
                            except AccessRoleRule.DoesNotExist:
                                continue
                    except BusinessElement.DoesNotExist:
                        pass
            
            # If user owns the object and has basic permission, allow
            if is_owner:
                return True
        
        # Check _all permissions
        return self.has_permission(request, view)


class IsAdmin(permissions.BasePermission):
    """Check if user has admin role"""
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'id'):
            raise AuthenticationFailed('Authentication required')
        
        from .models import UserRole, Role
        admin_role = Role.objects.filter(name='admin').first()
        if not admin_role:
            return False
        
        return UserRole.objects.filter(user=request.user, role=admin_role).exists()
