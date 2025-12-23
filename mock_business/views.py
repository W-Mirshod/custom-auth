from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from auth_system.permissions import HasElementPermission


@method_decorator(csrf_exempt, name='dispatch')
class ProductsListView(APIView):
    """Mock products endpoint with permission checks"""
    permission_classes = [HasElementPermission]
    permission_element = 'products'
    permission_action = 'read'
    
    def get(self, request):
        """Return mock products list"""
        # Mock products data
        products = [
            {
                'id': 1,
                'name': 'Laptop',
                'price': 999.99,
                'owner_id': 1,
                'description': 'High-performance laptop'
            },
            {
                'id': 2,
                'name': 'Smartphone',
                'price': 699.99,
                'owner_id': 2,
                'description': 'Latest smartphone model'
            },
            {
                'id': 3,
                'name': 'Tablet',
                'price': 399.99,
                'owner_id': request.user.id if request.user and hasattr(request.user, 'id') else None,
                'description': 'Portable tablet device'
            },
        ]
        
        # Filter based on permissions (if user has read_all, show all; otherwise show only own)
        if request.user and hasattr(request.user, 'id'):
            from auth_system.models import UserRole, AccessRoleRule, BusinessElement, Role
            element = BusinessElement.objects.get(name='products')
            user_roles = UserRole.objects.filter(user=request.user).select_related('role')
            
            has_read_all = False
            for user_role in user_roles:
                try:
                    rule = AccessRoleRule.objects.get(role=user_role.role, element=element)
                    if rule.read_all_permission:
                        has_read_all = True
                        break
                except AccessRoleRule.DoesNotExist:
                    continue
            
            if not has_read_all:
                # Show only user's own products
                products = [p for p in products if p.get('owner_id') == request.user.id]
        
        return Response({'products': products}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class ShopsListView(APIView):
    """Mock shops endpoint with permission checks"""
    permission_classes = [HasElementPermission]
    permission_element = 'shops'
    permission_action = 'read'
    
    def get(self, request):
        """Return mock shops list"""
        shops = [
            {
                'id': 1,
                'name': 'Tech Store',
                'address': '123 Main St',
                'owner_id': 1,
                'description': 'Electronics and gadgets'
            },
            {
                'id': 2,
                'name': 'Book Shop',
                'address': '456 Oak Ave',
                'owner_id': 2,
                'description': 'Books and magazines'
            },
            {
                'id': 3,
                'name': 'Coffee Shop',
                'address': '789 Pine Rd',
                'owner_id': request.user.id if request.user and hasattr(request.user, 'id') else None,
                'description': 'Coffee and pastries'
            },
        ]
        
        # Filter based on permissions
        if request.user and hasattr(request.user, 'id'):
            from auth_system.models import UserRole, AccessRoleRule, BusinessElement
            element = BusinessElement.objects.get(name='shops')
            user_roles = UserRole.objects.filter(user=request.user).select_related('role')
            
            has_read_all = False
            for user_role in user_roles:
                try:
                    rule = AccessRoleRule.objects.get(role=user_role.role, element=element)
                    if rule.read_all_permission:
                        has_read_all = True
                        break
                except AccessRoleRule.DoesNotExist:
                    continue
            
            if not has_read_all:
                shops = [s for s in shops if s.get('owner_id') == request.user.id]
        
        return Response({'shops': shops}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class OrdersListView(APIView):
    """Mock orders endpoint with permission checks"""
    permission_classes = [HasElementPermission]
    permission_element = 'orders'
    permission_action = 'read'
    
    def get(self, request):
        """Return mock orders list"""
        orders = [
            {
                'id': 1,
                'order_number': 'ORD-001',
                'total': 1299.98,
                'status': 'completed',
                'owner_id': 1,
                'items': ['Laptop', 'Mouse']
            },
            {
                'id': 2,
                'order_number': 'ORD-002',
                'total': 699.99,
                'status': 'pending',
                'owner_id': 2,
                'items': ['Smartphone']
            },
            {
                'id': 3,
                'order_number': 'ORD-003',
                'total': 399.99,
                'status': 'shipped',
                'owner_id': request.user.id if request.user and hasattr(request.user, 'id') else None,
                'items': ['Tablet']
            },
        ]
        
        # Filter based on permissions
        if request.user and hasattr(request.user, 'id'):
            from auth_system.models import UserRole, AccessRoleRule, BusinessElement
            element = BusinessElement.objects.get(name='orders')
            user_roles = UserRole.objects.filter(user=request.user).select_related('role')
            
            has_read_all = False
            for user_role in user_roles:
                try:
                    rule = AccessRoleRule.objects.get(role=user_role.role, element=element)
                    if rule.read_all_permission:
                        has_read_all = True
                        break
                except AccessRoleRule.DoesNotExist:
                    continue
            
            if not has_read_all:
                orders = [o for o in orders if o.get('owner_id') == request.user.id]
        
        return Response({'orders': orders}, status=status.HTTP_200_OK)
