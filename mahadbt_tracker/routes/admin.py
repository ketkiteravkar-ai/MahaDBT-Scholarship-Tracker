from functools import wraps
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from models import db, User, Scholarship, Application
from forms import ScholarshipForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator to require login and admin privileges."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@admin_required
def index():
    """Admin dashboard with overview statistics and scheme breakdowns."""
    total_students = User.query.filter_by(role='student').count()
    total_applications = Application.query.count()
    approved = Application.query.filter_by(status='approved').count()
    pending = Application.query.filter(Application.status.in_(['submitted', 'under_review', 'verified'])).count()
    rejected = Application.query.filter_by(status='rejected').count()

    # Application count grouped by scheme
    scheme_data = db.session.query(
        Scholarship.id,
        Scholarship.name,
        Scholarship.department,
        db.func.count(Application.id).label('app_count')
    ).outerjoin(Application, Scholarship.id == Application.scholarship_id
    ).group_by(Scholarship.id, Scholarship.name, Scholarship.department
    ).order_by(db.desc('app_count')).all()

    by_scheme = {item.name: item.app_count for item in scheme_data}

    stats = {
        'total_students': total_students,
        'total_applications': total_applications,
        'approved': approved,
        'pending': pending,
        'rejected': rejected,
        'by_scheme': by_scheme,
        'scheme_stats': scheme_data
    }

    recent_applications = Application.query.order_by(Application.applied_date.desc()).limit(8).all()

    return render_template('admin/index.html', stats=stats, recent_applications=recent_applications)


@admin_bp.route('/scholarships')
@admin_required
def scholarships():
    """List all scholarships in the system."""
    scholarships_list = Scholarship.query.order_by(Scholarship.created_at.desc()).all()
    return render_template('admin/scholarships.html', scholarships=scholarships_list)


@admin_bp.route('/scholarships/add', methods=['GET', 'POST'])
@admin_required
def add_scholarship():
    """Create a new scholarship scheme."""
    form = ScholarshipForm()
    if form.validate_on_submit():
        scholarship = Scholarship(
            name=form.name.data.strip(),
            department=form.department.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            eligibility_criteria=form.eligibility_criteria.data.strip() if form.eligibility_criteria.data else None,
            amount=form.amount.data,
            deadline=form.deadline.data,
            category_filter=form.category_filter.data,
            income_limit=form.income_limit.data,
            is_active=form.is_active.data
        )
        try:
            db.session.add(scholarship)
            db.session.commit()
            flash(f'Scholarship "{scholarship.name}" created successfully!', 'success')
            return redirect(url_for('admin.scholarships'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to create scholarship. Please check inputs and try again.', 'danger')

    return render_template('admin/scholarship_form.html', form=form, action='Add')


@admin_bp.route('/scholarships/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_scholarship(id):
    """Edit an existing scholarship scheme."""
    scholarship = Scholarship.query.get_or_404(id)
    form = ScholarshipForm(obj=scholarship)

    if form.validate_on_submit():
        scholarship.name = form.name.data.strip()
        scholarship.department = form.department.data.strip()
        scholarship.description = form.description.data.strip() if form.description.data else None
        scholarship.eligibility_criteria = form.eligibility_criteria.data.strip() if form.eligibility_criteria.data else None
        scholarship.amount = form.amount.data
        scholarship.deadline = form.deadline.data
        scholarship.category_filter = form.category_filter.data
        scholarship.income_limit = form.income_limit.data
        scholarship.is_active = form.is_active.data

        try:
            db.session.commit()
            flash(f'Scholarship "{scholarship.name}" updated successfully!', 'success')
            return redirect(url_for('admin.scholarships'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update scholarship. Please try again.', 'danger')

    return render_template('admin/scholarship_form.html', form=form, scholarship=scholarship, action='Edit')


@admin_bp.route('/scholarships/delete/<int:id>', methods=['POST'])
@admin_required
def delete_scholarship(id):
    """Delete a scholarship scheme."""
    scholarship = Scholarship.query.get_or_404(id)
    name = scholarship.name
    try:
        db.session.delete(scholarship)
        db.session.commit()
        flash(f'Scholarship "{name}" was successfully deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to delete scholarship "{name}".', 'danger')

    return redirect(url_for('admin.scholarships'))


@admin_bp.route('/review')
@admin_required
def review():
    """Review student applications with filtering by status and scholarship scheme."""
    status_filter = request.args.get('status', '').strip()
    scheme_filter = request.args.get('scheme', '').strip()

    query = Application.query.join(User).join(Scholarship)

    if status_filter:
        query = query.filter(Application.status == status_filter)

    if scheme_filter:
        if scheme_filter.isdigit():
            query = query.filter(Application.scholarship_id == int(scheme_filter))
        else:
            query = query.filter(Scholarship.name.ilike(f'%{scheme_filter}%'))

    applications = query.order_by(Application.applied_date.desc()).all()
    scholarships = Scholarship.query.order_by(Scholarship.name.asc()).all()

    return render_template(
        'admin/review.html',
        applications=applications,
        scholarships=scholarships,
        status_filter=status_filter,
        scheme_filter=scheme_filter
    )


@admin_bp.route('/review/<int:id>', methods=['POST'])
@admin_required
def update_review(id):
    """Update application status and remarks."""
    application = Application.query.get_or_404(id)
    new_status = request.form.get('status', '').strip()
    new_remarks = request.form.get('remarks', '').strip()

    valid_statuses = ['submitted', 'under_review', 'verified', 'approved', 'rejected']
    if new_status in valid_statuses:
        application.status = new_status

    application.remarks = new_remarks
    application.last_updated = datetime.utcnow()

    try:
        db.session.commit()
        flash(f'Application #{application.id} for {application.applicant.full_name} updated to "{application.status}".', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to update application review. Please try again.', 'danger')

    return redirect(url_for('admin.review'))
