"""Blueprint exports."""
from .site_controller import site_bp
from .auth_controller import auth_bp
from .resource_controller import resource_bp
from .dashboard_controller import dashboard_bp
from .booking_controller import booking_bp
from .message_controller import message_bp
from .review_controller import review_bp
from .admin_controller import admin_bp

__all__ = [
    'site_bp',
    'auth_bp',
    'resource_bp',
    'dashboard_bp',
    'booking_bp',
    'message_bp',
    'review_bp',
    'admin_bp',
]
