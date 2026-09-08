from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    FloatField,
    TextAreaField,
    SelectField,
    DateField,
    EmailField
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
    NumberRange,
    ValidationError
)
from models import User


class RegistrationForm(FlaskForm):
    full_name = StringField(
        'Full Name',
        validators=[DataRequired(message='Full name is required.'), Length(max=100)]
    )
    email = EmailField(
        'Email Address',
        validators=[
            DataRequired(message='Email address is required.'),
            Email(message='Please enter a valid email address.'),
            Length(max=120)
        ]
    )
    aadhaar = StringField(
        'Aadhaar Number',
        validators=[
            DataRequired(message='Aadhaar number is required.'),
            Length(min=12, max=12, message='Aadhaar must be exactly 12 digits.')
        ]
    )
    phone = StringField(
        'Phone Number',
        validators=[
            Optional(),
            Length(min=10, max=10, message='Phone number must be 10 digits.')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.'),
            Length(min=6, message='Password must be at least 6 characters long.')
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password.'),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    submit = SubmitField('Register')

    def validate_email(self, field):
        email_clean = field.data.strip().lower()
        if User.query.filter_by(email=email_clean).first():
            raise ValidationError('This email is already registered. Please login.')

    def validate_aadhaar(self, field):
        aadhaar_clean = field.data.strip()
        if not aadhaar_clean.isdigit():
            raise ValidationError('Aadhaar number must contain digits only.')
        if User.query.filter_by(aadhaar=aadhaar_clean).first():
            raise ValidationError('This Aadhaar number is already registered.')

    def validate_phone(self, field):
        if field.data:
            phone_clean = field.data.strip()
            if not phone_clean.isdigit():
                raise ValidationError('Phone number must contain digits only.')


class LoginForm(FlaskForm):
    email = EmailField(
        'Email Address',
        validators=[
            DataRequired(message='Email address is required.'),
            Email(message='Please enter a valid email address.')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Password is required.')]
    )
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ProfileForm(FlaskForm):
    full_name = StringField(
        'Full Name',
        validators=[DataRequired(message='Full name is required.'), Length(max=100)]
    )
    phone = StringField(
        'Phone Number',
        validators=[
            Optional(),
            Length(min=10, max=10, message='Phone number must be 10 digits.')
        ]
    )
    category = SelectField(
        'Category',
        choices=[
            ('', 'Select Category'),
            ('General', 'General'),
            ('SC', 'SC'),
            ('ST', 'ST'),
            ('OBC', 'OBC'),
            ('VJNT', 'VJNT'),
            ('SBC', 'SBC')
        ],
        validators=[Optional()]
    )
    annual_income = FloatField(
        'Annual Income (₹)',
        validators=[
            Optional(),
            NumberRange(min=0, message='Income must be a positive number.')
        ]
    )
    college_name = StringField(
        'College Name',
        validators=[Optional(), Length(max=200)]
    )
    course = StringField(
        'Course / Degree',
        validators=[Optional(), Length(max=100)]
    )
    year_of_study = SelectField(
        'Year of Study',
        choices=[
            ('', 'Select Year of Study'),
            ('1st', '1st Year'),
            ('2nd', '2nd Year'),
            ('3rd', '3rd Year'),
            ('4th', '4th Year'),
            ('5th', '5th Year')
        ],
        validators=[Optional()]
    )
    bank_account = StringField(
        'Bank Account Number',
        validators=[Optional(), Length(max=20)]
    )
    ifsc_code = StringField(
        'IFSC Code',
        validators=[Optional(), Length(max=11)]
    )
    submit = SubmitField('Update Profile')

    def validate_phone(self, field):
        if field.data:
            phone_clean = field.data.strip()
            if not phone_clean.isdigit():
                raise ValidationError('Phone number must contain digits only.')

    def validate_ifsc_code(self, field):
        if field.data:
            code = field.data.strip().upper()
            if len(code) != 11:
                raise ValidationError('IFSC code must be exactly 11 characters long.')


class ApplicationForm(FlaskForm):
    document = FileField(
        'Upload Supporting Document',
        validators=[
            Optional(),
            FileAllowed(
                ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'],
                'Allowed formats: PDF, JPG, JPEG, PNG, DOC, DOCX'
            )
        ]
    )
    submit = SubmitField('Submit Application')


class ScholarshipForm(FlaskForm):
    name = StringField(
        'Scholarship Name',
        validators=[DataRequired(message='Scholarship name is required.'), Length(max=200)]
    )
    department = StringField(
        'Department',
        validators=[DataRequired(message='Department is required.'), Length(max=100)]
    )
    description = TextAreaField(
        'Description',
        validators=[Optional()]
    )
    eligibility_criteria = TextAreaField(
        'Eligibility Criteria',
        validators=[Optional()]
    )
    amount = FloatField(
        'Scholarship Amount (₹)',
        validators=[
            DataRequired(message='Amount is required.'),
            NumberRange(min=0, message='Amount must be a non-negative number.')
        ]
    )
    deadline = DateField(
        'Application Deadline',
        validators=[Optional()],
        format='%Y-%m-%d'
    )
    category_filter = SelectField(
        'Category Filter',
        choices=[
            ('All', 'All Categories'),
            ('SC', 'SC'),
            ('ST', 'ST'),
            ('OBC', 'OBC'),
            ('VJNT', 'VJNT'),
            ('SBC', 'SBC'),
            ('General', 'General')
        ],
        default='All',
        validators=[DataRequired()]
    )
    income_limit = FloatField(
        'Annual Income Limit (₹)',
        validators=[
            Optional(),
            NumberRange(min=0, message='Income limit must be a positive number.')
        ]
    )
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Scholarship')


class ApplicationReviewForm(FlaskForm):
    status = SelectField(
        'Application Status',
        choices=[
            ('submitted', 'Submitted'),
            ('under_review', 'Under Review'),
            ('verified', 'Verified'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        validators=[DataRequired()]
    )
    remarks = TextAreaField(
        'Admin Remarks / Reason',
        validators=[Optional()]
    )
    submit = SubmitField('Update Status')
