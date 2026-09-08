from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    aadhaar = db.Column(db.String(12), unique=True)
    phone = db.Column(db.String(10))
    category = db.Column(db.String(20))  # SC, ST, OBC, VJNT, SBC, General
    annual_income = db.Column(db.Float)
    college_name = db.Column(db.String(200))
    course = db.Column(db.String(100))
    year_of_study = db.Column(db.String(20))
    bank_account = db.Column(db.String(20))
    ifsc_code = db.Column(db.String(11))
    role = db.Column(db.String(10), default='student')  # student or admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applications = db.relationship('Application', backref='applicant', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class Scholarship(db.Model):
    __tablename__ = 'scholarship'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    eligibility_criteria = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    deadline = db.Column(db.Date)
    category_filter = db.Column(db.String(50))  # comma-separated: SC,ST,OBC or 'All'
    income_limit = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applications = db.relationship('Application', backref='scholarship', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Scholarship {self.name}>'


class Application(db.Model):
    __tablename__ = 'application'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scholarship_id = db.Column(db.Integer, db.ForeignKey('scholarship.id'), nullable=False)
    status = db.Column(db.String(20), default='submitted')  # submitted, under_review, verified, approved, rejected
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    remarks = db.Column(db.Text)
    document_path = db.Column(db.String(300))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Application User:{self.user_id} Scholarship:{self.scholarship_id} Status:{self.status}>'
