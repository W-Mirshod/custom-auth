from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import AccessRoleRule, Role, BusinessElement
from .permissions import IsAdmin


class AccessRoleRuleSerializer(serializers.ModelSerializer):
    """Serializer for AccessRoleRule"""
    role_name = serializers.CharField(source='role.name', read_only=True)
    element_name = serializers.CharField(source='element.name', read_only=True)
    
    class Meta:
        model = AccessRoleRule
        fields = [
            'id', 'role', 'role_name', 'element', 'element_name',
            'read_permission', 'read_all_permission',
            'create_permission',
            'update_permission', 'update_all_permission',
            'delete_permission', 'delete_all_permission'
        ]
        read_only_fields = ['id']


class AccessRoleRuleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating AccessRoleRule"""
    class Meta:
        model = AccessRoleRule
        fields = [
            'role', 'element',
            'read_permission', 'read_all_permission',
            'create_permission',
            'update_permission', 'update_all_permission',
            'delete_permission', 'delete_all_permission'
        ]
    
    def validate(self, data):
        """Check if rule already exists"""
        if self.instance is None:  # Creating new
            if AccessRoleRule.objects.filter(role=data['role'], element=data['element']).exists():
                raise serializers.ValidationError("Access rule for this role and element already exists")
        return data


@method_decorator(csrf_exempt, name='dispatch')
class AccessRulesListView(APIView):
    """List all access rules (admin only)"""
    permission_classes = [IsAdmin]
    
    def get(self, request):
        """Get all access rules"""
        rules = AccessRoleRule.objects.select_related('role', 'element').all()
        serializer = AccessRoleRuleSerializer(rules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Create a new access rule"""
        serializer = AccessRoleRuleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            rule = AccessRoleRule.objects.get(pk=serializer.instance.pk)
            response_serializer = AccessRoleRuleSerializer(rule)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class AccessRuleDetailView(APIView):
    """Retrieve, update, or delete an access rule (admin only)"""
    permission_classes = [IsAdmin]
    
    def get(self, request, pk):
        """Get a specific access rule"""
        try:
            rule = AccessRoleRule.objects.select_related('role', 'element').get(pk=pk)
            serializer = AccessRoleRuleSerializer(rule)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AccessRoleRule.DoesNotExist:
            return Response({'error': 'Access rule not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, pk):
        """Update an access rule"""
        try:
            rule = AccessRoleRule.objects.get(pk=pk)
            serializer = AccessRoleRuleCreateSerializer(rule, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                updated_rule = AccessRoleRule.objects.select_related('role', 'element').get(pk=pk)
                response_serializer = AccessRoleRuleSerializer(updated_rule)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AccessRoleRule.DoesNotExist:
            return Response({'error': 'Access rule not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        """Delete an access rule"""
        try:
            rule = AccessRoleRule.objects.get(pk=pk)
            rule.delete()
            return Response({'message': 'Access rule deleted successfully'}, status=status.HTTP_200_OK)
        except AccessRoleRule.DoesNotExist:
            return Response({'error': 'Access rule not found'}, status=status.HTTP_404_NOT_FOUND)
