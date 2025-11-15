"""Booking workflows."""
from __future__ import annotations

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.data_access.booking_dal import BookingDAL
from src.data_access.notification_dal import NotificationDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.user_dal import UserDAL

booking_bp = Blueprint('booking', __name__, url_prefix='/bookings')
APPROVER_ROLES = {'staff', 'admin'}


def _parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _user_can_approve(user) -> bool:
    return user.is_authenticated and user.role in APPROVER_ROLES


def _require_approver_role():
    if not _user_can_approve(current_user):
        flash('Only staff and admin users can review booking requests.', 'danger')
        return False
    return True


@booking_bp.route('/request/<int:resource_id>', methods=['GET', 'POST'])
@login_required
def request_booking(resource_id: int):
    resource = ResourceDAL.get_resource_by_id(resource_id)
    if not resource or resource.status != 'published':
        flash('Resource is not available for booking.', 'warning')
        return redirect(url_for('resource.browse'))
    owner_user = UserDAL.get_user_by_id(resource.owner_id)

    if request.method == 'POST':
        start_raw = request.form.get('start_datetime')
        end_raw = request.form.get('end_datetime')
        notes = request.form.get('notes', '').strip() or None

        start_dt = _parse_datetime(start_raw)
        end_dt = _parse_datetime(end_raw)
        if not start_dt or not end_dt:
            flash('Please provide valid start and end times.', 'danger')
            return render_template('bookings/form.html', resource=resource, form=request.form)
        if end_dt <= start_dt:
            flash('End time must be after the start time.', 'danger')
            return render_template('bookings/form.html', resource=resource, form=request.form)

        if BookingDAL.has_conflict(resource.resource_id, start_dt.isoformat(), end_dt.isoformat()):
            flash('Another booking overlaps with those times. Try a different slot.', 'warning')
            return render_template('bookings/form.html', resource=resource, form=request.form)

        status = 'pending'
        if resource.owner_id == current_user.user_id and _user_can_approve(current_user):
            status = 'approved'

        booking = BookingDAL.create_booking(
            resource_id=resource.resource_id,
            requester_id=current_user.user_id,
            start=start_dt.isoformat(),
            end=end_dt.isoformat(),
            notes=notes,
            status=status
        )

        if resource.owner_id != current_user.user_id and owner_user:
            NotificationDAL.create_notification(
                resource.owner_id,
                f'New booking request for {resource.title} from {current_user.name}.'
            )

        flash('Booking submitted.', 'success')
        return redirect(url_for('booking.my_bookings'))

    return render_template('bookings/form.html', resource=resource, form={})


@booking_bp.route('/mine')
@login_required
def my_bookings():
    bookings = BookingDAL.get_bookings_by_requester(current_user.user_id)
    resources = {b.resource_id: ResourceDAL.get_resource_by_id(b.resource_id) for b in bookings}
    return render_template('bookings/list.html', bookings=bookings, resources=resources)


@booking_bp.route('/inbox')
@login_required
def owner_inbox():
    if not _require_approver_role():
        return redirect(url_for('booking.my_bookings'))
    pending = BookingDAL.get_actionable_for_owner(current_user.user_id)
    resources = {b.resource_id: ResourceDAL.get_resource_by_id(b.resource_id) for b in pending}
    return render_template('bookings/owner_queue.html', bookings=pending, resources=resources)


@booking_bp.route('/<int:booking_id>/decision', methods=['POST'])
@login_required
def decide_booking(booking_id: int):
    booking = BookingDAL.get_booking_by_id(booking_id)
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('booking.owner_inbox'))

    resource = ResourceDAL.get_resource_by_id(booking.resource_id)
    if not resource or resource.owner_id != current_user.user_id:
        flash('You do not manage that booking.', 'danger')
        return redirect(url_for('booking.owner_inbox'))
    if not _user_can_approve(current_user):
        flash('Only staff and admin users can approve or reject bookings.', 'danger')
        return redirect(url_for('booking.owner_inbox'))

    action = request.form.get('action')
    note = request.form.get('owner_notes', '').strip() or None
    if action not in {'approve', 'reject'}:
        flash('Invalid action.', 'danger')
        return redirect(url_for('booking.owner_inbox'))

    new_status = 'approved' if action == 'approve' else 'rejected'
    BookingDAL.update_status(booking_id, new_status, owner_notes=note)
    NotificationDAL.create_notification(
        booking.requester_id,
        f'Your booking for {resource.title} was {new_status}.'
    )
    flash(f'Booking {new_status}.', 'success')
    return redirect(url_for('booking.owner_inbox'))
