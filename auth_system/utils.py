import bcrypt
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Session, User


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def create_session(user: User) -> Session:
    """Create a new session for a user"""
    # Delete expired sessions for this user
    Session.objects.filter(user=user, expires_at__lt=timezone.now()).delete()
    
    # Create new session
    expires_at = timezone.now() + timedelta(seconds=settings.SESSION_EXPIRE_SECONDS)
    session = Session.objects.create(
        user=user,
        expires_at=expires_at
    )
    return session


def get_session_by_id(session_id: str) -> Session | None:
    """Get a session by session_id, checking if it's expired"""
    try:
        session = Session.objects.get(session_id=session_id)
        if session.is_expired():
            session.delete()
            return None
        return session
    except Session.DoesNotExist:
        return None


def delete_session(session_id: str) -> bool:
    """Delete a session by session_id"""
    try:
        session = Session.objects.get(session_id=session_id)
        session.delete()
        return True
    except Session.DoesNotExist:
        return False


def delete_all_user_sessions(user: User):
    """Delete all sessions for a user"""
    Session.objects.filter(user=user).delete()
