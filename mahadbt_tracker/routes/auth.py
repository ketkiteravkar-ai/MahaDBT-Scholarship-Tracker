from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User
from forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
@auth_bp.route('/auth/register', methods=['GET', 'POST'])
def register():
    """Register a new student account."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.index'))
        return redirect(url_for('student.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            password_hash=generate_password_hash(form.password.data),
            aadhaar=form.aadhaar.data.strip(),
            phone=form.phone.data.strip() if form.phone.data else None,
            role='student'
        )
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login with your email and password.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
@auth_bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    """Authenticate user and redirect to appropriate dashboard."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.index'))
        return redirect(url_for('student.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            remember = form.remember.data if hasattr(form, 'remember') else False
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.full_name}!', 'success')

            # Redirect to next url if safe
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)

            if user.role == 'admin':
                return redirect(url_for('admin.index'))
            return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid email or password. Please verify your credentials and try again.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@auth_bp.route('/auth/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
