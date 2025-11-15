"""Dashboard routes for authenticated users."""
from datetime import datetime

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from src.data_access.booking_dal import BookingDAL
from src.data_access.notification_dal import NotificationDAL
from src.data_access.resource_dal import ResourceDAL


dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def overview():
    BookingDAL.mark_completed_for_past_reservations(datetime.utcnow().isoformat())
    listings = ResourceDAL.get_resources_by_owner(current_user.user_id)
    spotlight = ResourceDAL.get_featured_resources(limit=3)
    my_bookings = BookingDAL.get_bookings_by_requester(current_user.user_id)
    pending_actions = BookingDAL.get_actionable_for_owner(current_user.user_id)
    notifications = NotificationDAL.list_for_user(current_user.user_id)
    return render_template(
        'dashboard/overview.html',
        listings=listings,
        spotlight=spotlight,
        my_bookings=my_bookings,
        pending_actions=pending_actions,
        notifications=notifications,
    )
