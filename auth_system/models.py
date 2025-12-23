from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid


class User(models.Model):
    """Custom User model for authentication"""
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    patronymic = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Session(models.Model):
    """Custom session model for session-based authentication"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sessions'
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Session {self.session_id} for {self.user.email}"

    def is_expired(self):
        """Check if session has expired"""
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        """Set expiration time on creation"""
        if not self.pk:
            self.expires_at = timezone.now() + timedelta(seconds=7 * 24 * 60 * 60)  # 7 days
        super().save(*args, **kwargs)


class Role(models.Model):
    """User roles (admin, manager, user, guest)"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'roles'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """Many-to-many relationship between users and roles"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')

    class Meta:
        db_table = 'user_roles'
        unique_together = ['user', 'role']
        indexes = [
            models.Index(fields=['user', 'role']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"


class BusinessElement(models.Model):
    """Business entities that require access control"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'business_elements'
        ordering = ['name']

    def __str__(self):
        return self.name


class AccessRoleRule(models.Model):
    """Access control rules defining permissions for roles on business elements"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='access_rules')
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE, related_name='access_rules')
    
    # Permission flags
    read_permission = models.BooleanField(default=False)
    read_all_permission = models.BooleanField(default=False)
    create_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)
    delete_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)

    class Meta:
        db_table = 'access_roles_rules'
        unique_together = ['role', 'element']
        indexes = [
            models.Index(fields=['role', 'element']),
        ]

    def __str__(self):
        return f"{self.role.name} -> {self.element.name}"
