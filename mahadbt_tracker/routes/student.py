import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models import db, Scholarship, Application
from forms import ProfileForm, ApplicationForm

student_bp = Blueprint('student', __name__)


@student_bp.route('/')
def index():
    """Landing route: redirect authenticated users to dashboard or guests to login."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.index'))
        return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))


@student_bp.route('/dashboard')
@login_required
def dashboard():
    """Student dashboard showing application statistics and recent activity."""
    if current_user.role == 'admin':
        return redirect(url_for('admin.index'))

    applications = Application.query.filter_by(user_id=current_user.id).order_by(Application.applied_date.desc()).all()

    stats = {
        'total': len(applications),
        'approved': sum(1 for app in applications if app.status == 'approved'),
        'pending': sum(1 for app in applications if app.status in ('submitted', 'under_review', 'verified')),
        'rejected': sum(1 for app in applications if app.status == 'rejected')
    }

    # Available scholarships for recommendation
    available_scholarships = Scholarship.query.filter_by(is_active=True).order_by(Scholarship.deadline.asc()).limit(4).all()
    applied_scholarship_ids = {app.scholarship_id for app in applications}

    return render_template(
        'student/dashboard.html',
        applications=applications,
        stats=stats,
        available_scholarships=available_scholarships,
        applied_scholarship_ids=applied_scholarship_ids
    )


@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and update student profile information."""
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.phone = form.phone.data.strip() if form.phone.data else None
        current_user.category = form.category.data if form.category.data else None
        current_user.annual_income = form.annual_income.data
        current_user.college_name = form.college_name.data.strip() if form.college_name.data else None
        current_user.course = form.course.data.strip() if form.course.data else None
        current_user.year_of_study = form.year_of_study.data if form.year_of_study.data else None
        current_user.bank_account = form.bank_account.data.strip() if form.bank_account.data else None
        current_user.ifsc_code = form.ifsc_code.data.strip().upper() if form.ifsc_code.data else None

        try:
            db.session.commit()
            flash('Your profile has been updated successfully!', 'success')
            return redirect(url_for('student.profile'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile. Please try again.', 'danger')

    return render_template('student/profile.html', form=form)


@student_bp.route('/scholarships')
@login_required
def scholarships():
    """Browse and filter active scholarships."""
    category_filter = request.args.get('category', '').strip()
    query = Scholarship.query.filter_by(is_active=True)

    if category_filter and category_filter != 'All':
        query = query.filter(
            db.or_(
                Scholarship.category_filter == 'All',
                Scholarship.category_filter.ilike(f'%{category_filter}%')
            )
        )

    scholarships_list = query.order_by(Scholarship.deadline.asc()).all()
    categories = ['All', 'SC', 'ST', 'OBC', 'VJNT', 'SBC', 'General']

    applied_scholarship_ids = {app.scholarship_id for app in current_user.applications}

    return render_template(
        'student/scholarships.html',
        scholarships=scholarships_list,
        categories=categories,
        selected_category=category_filter or 'All',
        applied_scholarship_ids=applied_scholarship_ids
    )


@student_bp.route('/apply/<int:scholarship_id>', methods=['GET', 'POST'])
@login_required
def apply(scholarship_id):
    """Apply for a specific scholarship with document upload."""
    scholarship = Scholarship.query.get_or_404(scholarship_id)

    # Check if already applied
    existing_application = Application.query.filter_by(
        user_id=current_user.id,
        scholarship_id=scholarship_id
    ).first()

    if existing_application:
        flash(f'You have already submitted an application for "{scholarship.name}".', 'warning')
        return redirect(url_for('student.track'))

    form = ApplicationForm()
    if form.validate_on_submit():
        document_filename = None
        if form.document.data:
            uploaded_file = form.document.data
            clean_filename = secure_filename(uploaded_file.filename)
            if clean_filename:
                timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                document_filename = f"user_{current_user.id}_sch_{scholarship_id}_{timestamp}_{clean_filename}"
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document_filename)
                uploaded_file.save(save_path)

        application = Application(
            user_id=current_user.id,
            scholarship_id=scholarship_id,
            status='submitted',
            applied_date=datetime.utcnow(),
            document_path=document_filename
        )

        try:
            db.session.add(application)
            db.session.commit()
            flash(f'Application for "{scholarship.name}" submitted successfully!', 'success')
            return redirect(url_for('student.track'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to submit application. Please try again.', 'danger')

    return render_template('student/apply.html', scholarship=scholarship, form=form)


@student_bp.route('/track')
@login_required
def track():
    """Track the status and remarks of all submitted applications."""
    applications = Application.query.filter_by(user_id=current_user.id).order_by(Application.applied_date.desc()).all()
    return render_template('student/track.html', applications=applications)
