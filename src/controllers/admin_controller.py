"""Admin dashboard routes."""
from functools import wraps
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.data_access.booking_dal import BookingDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.review_dal import ReviewDAL
from src.data_access.user_dal import UserDAL

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('site.home'))
        return func(*args, **kwargs)
    return login_required(wrapper)


@admin_bp.route('/')
@admin_required
def dashboard():
    users = UserDAL.list_users()
    resources = ResourceDAL.search_resources(status=None)
    bookings = BookingDAL.list_recent()
    reviews = ReviewDAL.list_recent()
    stats = {
        'total_users': len(users),
        'total_resources': len(resources),
        'pending_requests': len([b for b in bookings if b.status == 'pending']),
    }
    return render_template('admin/dashboard.html', users=users, resources=resources, bookings=bookings, reviews=reviews, stats=stats)


@admin_bp.route('/bookings/<int:booking_id>/status', methods=['POST'])
@admin_required
def override_booking(booking_id: int):
    new_status = request.form.get('status')
    if new_status not in BookingDAL.STATUSES:
        flash('Invalid status.', 'danger')
        return redirect(url_for('admin.dashboard'))
    BookingDAL.update_status(booking_id, new_status, owner_notes='Updated by admin')
    flash('Booking updated.', 'success')
    return redirect(url_for('admin.dashboard'))
