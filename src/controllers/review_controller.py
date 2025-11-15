"""Review routes."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.data_access.booking_dal import BookingDAL
from src.data_access.review_dal import ReviewDAL
from src.data_access.resource_dal import ResourceDAL
from src.utils.validators import Validator

review_bp = Blueprint('review', __name__, url_prefix='/reviews')


def _user_completed_booking(resource_id: int, user_id: int) -> bool:
    bookings = BookingDAL.get_bookings_by_requester(user_id)
    for booking in bookings:
        if booking.resource_id == resource_id and booking.status == 'completed':
            return True
    return False


@review_bp.route('/create/<int:resource_id>', methods=['GET', 'POST'])
@login_required
def create(resource_id: int):
    resource = ResourceDAL.get_resource_by_id(resource_id)
    if not resource or resource.status != 'published':
        flash('Resource not available for review.', 'warning')
        return redirect(url_for('resource.browse'))

    if not _user_completed_booking(resource_id, current_user.user_id):
        flash('Complete a booking before posting a review.', 'info')
        return redirect(url_for('resource.detail', resource_id=resource_id))

    if ReviewDAL.user_has_reviewed(resource_id, current_user.user_id):
        flash('You have already reviewed this resource.', 'info')
        return redirect(url_for('resource.detail', resource_id=resource_id))

    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment', '').strip() or None
        valid, parsed = Validator.validate_integer(rating, 1, 5, 'Rating')
        if not valid:
            flash(parsed, 'danger')
            return render_template('reviews/form.html', resource=resource)

        if comment:
            valid, message = Validator.validate_string(comment, 5, 1200, 'Comment')
            if not valid:
                flash(message, 'danger')
                return render_template('reviews/form.html', resource=resource)

        ReviewDAL.create_review(resource_id, current_user.user_id, parsed, comment)
        flash('Review published.', 'success')
        return redirect(url_for('resource.detail', resource_id=resource_id))

    return render_template('reviews/form.html', resource=resource)


@review_bp.route('/<int:review_id>/delete', methods=['POST'])
@login_required
def delete(review_id: int):
    review = ReviewDAL.get_review_by_id(review_id)
    if not review:
        flash('Review not found.', 'danger')
        return redirect(url_for('dashboard.overview'))

    if review.reviewer_id != current_user.user_id and current_user.role != 'admin':
        flash('You cannot delete that review.', 'danger')
        return redirect(url_for('resource.detail', resource_id=review.resource_id))

    ReviewDAL.delete_review(review_id)
    flash('Review removed.', 'info')
    return redirect(url_for('resource.detail', resource_id=review.resource_id))
