from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .utils import get_session_by_id


class SessionMiddleware(MiddlewareMixin):
    """Custom middleware to handle session-based authentication"""
    
    def process_request(self, request):
        """Process incoming request and attach user if session is valid"""
        request.session_obj = None
        
        # Get session_id from cookie
        session_id = request.COOKIES.get('sessionid')
        
        if not session_id:
            return None
        
        # Try to get session
        try:
            session = get_session_by_id(session_id)
            if session and not session.is_expired():
                request.user = session.user
                request.session_obj = session
                # Update last_accessed_at
                session.save(update_fields=['last_accessed_at'])
            else:
                # Session expired or invalid - don't set to None, let REST Framework handle it
                request.session_obj = None
        except Exception as e:
            # On error, don't modify request.user
            request.session_obj = None
        
        return None
    
    def process_response(self, request, response):
        """Process outgoing response"""
        # Middleware can modify response here if needed
        return response
