from django.utils.deprecation import MiddlewareMixin
from .utils import get_session_by_id


class SessionMiddleware(MiddlewareMixin):
    """Custom middleware to handle session-based authentication"""
    
    def process_request(self, request):
        """Process incoming request and attach user if session is valid"""
        # Initialize request.user as None
        request.user = None
        request.session_obj = None
        
        # Get session_id from cookie
        session_id = request.COOKIES.get('sessionid')
        
        if not session_id:
            return None  # No session, continue processing (will be handled by views)
        
        # Try to get session
        try:
            session = get_session_by_id(session_id)
            if session and not session.is_expired():
                request.user = session.user
                request.session_obj = session
                # Update last_accessed_at
                session.save(update_fields=['last_accessed_at'])
            else:
                # Session expired or invalid
                request.user = None
                request.session_obj = None
        except Exception:
            request.user = None
            request.session_obj = None
        
        return None
    
    def process_response(self, request, response):
        """Process outgoing response"""
        # Middleware can modify response here if needed
        return response
