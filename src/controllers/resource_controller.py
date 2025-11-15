"""Resource management routes."""
from __future__ import annotations

import os
from typing import List

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from src.data_access.resource_dal import ResourceDAL
from src.data_access.review_dal import ReviewDAL
from src.utils.validators import Validator

resource_bp = Blueprint('resource', __name__)

RESOURCE_CATEGORIES = [
    'Study Room',
    'Event Space',
    'Lab Equipment',
    'Tutoring',
    'AV Equipment',
    'Community Resource',
]
RESOURCE_STATUSES = ['draft', 'published', 'archived']
BLANK_FORM = {
    'title': '',
    'summary': '',
    'category': RESOURCE_CATEGORIES[0],
    'location': '',
    'capacity': '',
    'availability_notes': '',
    'status': 'draft',
}
RESOURCE_OWNER_ROLES = {'staff', 'admin'}


def _save_images(files) -> List[str]:
    saved = []
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    for file in files:
        if not file or not file.filename:
            continue
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[-1].lower()
        if ext not in current_app.config['ALLOWED_EXTENSIONS']:
            raise ValueError('Unsupported file type uploaded.')
        path = os.path.join(upload_dir, filename)
        counter = 1
        while os.path.exists(path):
            name, extension = os.path.splitext(filename)
            new_name = f"{name}_{counter}{extension}"
            path = os.path.join(upload_dir, new_name)
            counter += 1
        file.save(path)
        relative_path = os.path.relpath(path, start=os.path.join(current_app.root_path, 'static'))
        saved.append(relative_path.replace('\\', '/'))
    return saved


def _require_resource_owner_role():
    if not _user_can_manage_resources():
        flash('Only staff and admin users can manage resources.', 'danger')
        return False
    return True


def _user_can_manage_resources() -> bool:
    return current_user.is_authenticated and current_user.role in RESOURCE_OWNER_ROLES


@resource_bp.route('/')
def browse():
    filters = {
        'keyword': request.args.get('keyword', '').strip(),
        'category': request.args.get('category', '').strip(),
        'location': request.args.get('location', '').strip(),
        'min_capacity': request.args.get('min_capacity', '').strip(),
        'status': 'published'
    }

    min_capacity = None
    if filters['min_capacity']:
        valid, value = Validator.validate_integer(filters['min_capacity'], 1, 5000, 'Capacity')
        if valid:
            min_capacity = value
        else:
            flash(value, 'warning')

    resources = ResourceDAL.search_resources(
        keyword=filters['keyword'] or None,
        category=filters['category'] or None,
        location=filters['location'] or None,
        min_capacity=min_capacity,
        status='published',
    )

    return render_template(
        'resources/list.html',
        resources=resources,
        filters=filters,
        categories=RESOURCE_CATEGORIES,
    )


@resource_bp.route('/mine')
@login_required
def my_resources():
    if not _require_resource_owner_role():
        return redirect(url_for('dashboard.overview'))
    resources = ResourceDAL.get_resources_by_owner(current_user.user_id)
    return render_template(
        'resources/mine.html',
        resources=resources,
        statuses=RESOURCE_STATUSES,
    )


@resource_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not _require_resource_owner_role():
        return redirect(url_for('resource.browse'))
    if request.method == 'POST':
        form_data = _extract_form_data(request.form)
        errors = _validate_resource_form(form_data)
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('resources/form.html', form=form_data, categories=RESOURCE_CATEGORIES)

        try:
            gallery = _save_images(request.files.getlist('images'))
        except ValueError as exc:
            flash(str(exc), 'danger')
            return render_template('resources/form.html', form=form_data, categories=RESOURCE_CATEGORIES)

        resource = ResourceDAL.create_resource(
            owner_id=current_user.user_id,
            **form_data,
            gallery=gallery,
        )
        flash('Resource created.', 'success')
        if resource.status == 'published':
            return redirect(url_for('resource.detail', resource_id=resource.resource_id))
        return redirect(url_for('resource.my_resources'))

    return render_template('resources/form.html', form=dict(BLANK_FORM), categories=RESOURCE_CATEGORIES)


@resource_bp.route('/<int:resource_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(resource_id: int):
    resource = ResourceDAL.get_resource_by_id(resource_id)
    if not resource or resource.owner_id != current_user.user_id:
        flash('You do not have permission to edit that listing.', 'danger')
        return redirect(url_for('resource.browse'))
    if current_user.role not in RESOURCE_OWNER_ROLES:
        flash('Only staff and admin users can edit listings.', 'danger')
        return redirect(url_for('resource.detail', resource_id=resource_id))

    if request.method == 'POST':
        form_data = _extract_form_data(request.form)
        errors = _validate_resource_form(form_data)
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('resources/form.html', form=form_data, categories=RESOURCE_CATEGORIES, resource=resource)

        try:
            new_gallery = _save_images(request.files.getlist('images'))
        except ValueError as exc:
            flash(str(exc), 'danger')
            return render_template('resources/form.html', form=form_data, categories=RESOURCE_CATEGORIES, resource=resource)

        ResourceDAL.update_resource(resource_id, gallery=new_gallery or resource.gallery, **form_data)
        flash('Resource updated.', 'success')
        return redirect(url_for('resource.detail', resource_id=resource_id))

    form_defaults = {
        'title': resource.title,
        'summary': resource.summary,
        'category': resource.category,
        'location': resource.location,
        'capacity': resource.capacity,
        'availability_notes': resource.availability_notes,
        'status': resource.status,
    }
    return render_template('resources/form.html', form=form_defaults, categories=RESOURCE_CATEGORIES, resource=resource)


@resource_bp.route('/<int:resource_id>')
def detail(resource_id: int):
    resource = ResourceDAL.get_resource_by_id(resource_id)
    if not resource:
        flash('Resource not found.', 'warning')
        return redirect(url_for('resource.browse'))

    if resource.status != 'published' and (
        not current_user.is_authenticated or resource.owner_id != current_user.user_id
    ):
        flash('This listing is not currently available.', 'warning')
        return redirect(url_for('resource.browse'))

    related = ResourceDAL.get_related_resources(resource.category, exclude_id=resource_id)
    reviews = ReviewDAL.list_for_resource(resource_id)
    rating_stats = ReviewDAL.get_average_for_resource(resource_id)
    return render_template('resources/detail.html', resource=resource, related=related, reviews=reviews, rating_stats=rating_stats)


def _extract_form_data(form):
    return {
        'title': form.get('title', '').strip(),
        'summary': form.get('summary', '').strip(),
        'category': form.get('category', '').strip(),
        'location': form.get('location', '').strip(),
        'capacity': form.get('capacity', '').strip(),
        'availability_notes': form.get('availability_notes', '').strip() or None,
        'status': form.get('status', 'draft').strip() or 'draft',
    }


def _validate_resource_form(data):
    errors = []
    required_fields = {
        'title': (3, 120),
        'summary': (20, 1200),
        'location': (2, 120),
    }

    for field, (min_len, max_len) in required_fields.items():
        valid, message = Validator.validate_string(data[field], min_len, max_len, field.title())
        if not valid:
            errors.append(message)

    if data['category'] not in RESOURCE_CATEGORIES:
        errors.append('Please select a valid category.')

    if data['status'] not in RESOURCE_STATUSES:
        errors.append('Select a valid status (draft, published, or archived).')

    valid, value = Validator.validate_integer(data['capacity'], 1, 5000, 'Capacity')
    if not valid:
        errors.append(value)
    else:
        data['capacity'] = value

    return errors
