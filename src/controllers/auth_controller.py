"""Authentication routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user

from src.data_access.user_dal import UserDAL
from src.utils.validators import Validator

auth_bp = Blueprint('auth', __name__)
AVAILABLE_SIGNUP_ROLES = {'student', 'staff'}


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.overview'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        department = request.form.get('department', '').strip()
        role_input = request.form.get('role', 'student').strip().lower()
        role = role_input if role_input in AVAILABLE_SIGNUP_ROLES else 'student'

        valid, message = Validator.validate_string(name, 2, 120, 'Name')
        if not valid:
            flash(message, 'danger')
            return render_template('auth/register.html', form=request.form)

        if not Validator.validate_email(email):
            flash('Please supply a university email address.', 'danger')
            return render_template('auth/register.html', form=request.form)

        allowed_domains = current_app.config.get('ALLOWED_EMAIL_DOMAINS')
        if allowed_domains:
            if email.split('@')[-1] not in allowed_domains:
                flash('Only institutional email addresses may be used.', 'warning')
                return render_template('auth/register.html', form=request.form)

        valid, message = Validator.validate_password(password)
        if not valid:
            flash(message, 'danger')
            return render_template('auth/register.html', form=request.form)

        if password != confirm_password:
            flash('Passwords must match exactly.', 'danger')
            return render_template('auth/register.html', form=request.form)

        if department:
            valid, message = Validator.validate_string(department, 2, 120, 'Department')
            if not valid:
                flash(message, 'danger')
                return render_template('auth/register.html', form=request.form)

        existing = UserDAL.get_user_by_email(email)
        if existing:
            flash('An account already exists for that email.', 'danger')
            return render_template('auth/register.html', form=request.form)

        if role_input not in AVAILABLE_SIGNUP_ROLES:
            flash('Please select a valid role.', 'danger')
            return render_template('auth/register.html', form=request.form)

        user = UserDAL.create_user(
            name=name,
            email=email,
            password=password,
            role=role,
            department=department or None,
        )
        login_user(user)
        flash('Welcome aboard! Start by creating your first resource listing.', 'success')
        return redirect(url_for('dashboard.overview'))

    return render_template('auth/register.html', form={})


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.overview'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('auth/login.html', form=request.form)

        user = UserDAL.verify_password(email, password)
        if not user:
            flash('Invalid credentials. Please try again.', 'danger')
            return render_template('auth/login.html', form=request.form)

        login_user(user, remember=remember)
        flash('Signed in successfully.', 'success')
        return redirect(url_for('dashboard.overview'))

    return render_template('auth/login.html', form={})


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Signed out. Come back soon!', 'info')
    return redirect(url_for('site.home'))
