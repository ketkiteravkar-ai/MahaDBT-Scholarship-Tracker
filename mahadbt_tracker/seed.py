from datetime import date
from werkzeug.security import generate_password_hash

from app import app
from models import db, User, Scholarship, Application


def seed():
    """Seed the MahaDBT database with initial tables, admin user, demo student, and scholarship schemes."""
    with app.app_context():
        print("Initializing database tables...")
        db.create_all()

        # Seed Admin User
        admin_email = 'admin@mahadbt.gov.in'
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                full_name='Admin',
                email=admin_email,
                password_hash=generate_password_hash('admin123'),
                aadhaar='100000000001',
                phone='9876543210',
                role='admin'
            )
            db.session.add(admin)
            print(f"✓ Created Admin user: {admin_email} (password: admin123)")
        else:
            print(f"- Admin user already exists: {admin_email}")

        # Seed Demo Student User for testing convenience
        demo_student_email = 'student@mahadbt.gov.in'
        demo_student = User.query.filter_by(email=demo_student_email).first()
        if not demo_student:
            demo_student = User(
                full_name='Rahul Patil',
                email=demo_student_email,
                password_hash=generate_password_hash('student123'),
                aadhaar='200000000002',
                phone='9823456789',
                category='OBC',
                annual_income=250000.0,
                college_name='COEP Technological University, Pune',
                course='B.Tech Computer Engineering',
                year_of_study='3rd',
                bank_account='912345678901',
                ifsc_code='MAHB0000123',
                role='student'
            )
            db.session.add(demo_student)
            print(f"✓ Created Demo Student user: {demo_student_email} (password: student123)")
        else:
            print(f"- Demo student already exists: {demo_student_email}")

        # Seed 6 Standard MahaDBT Scholarships
        default_deadline = date(2026, 12, 31)

        scholarships_list = [
            {
                "name": "Rajarshi Chhatrapati Shahu Maharaj Shikshan Shulkh Scholarship",
                "department": "Social Justice and Special Assistance Department",
                "description": "Financial assistance for tuition and examination fees for students from SC category pursuing higher professional and non-professional courses in Maharashtra.",
                "eligibility_criteria": "Applicant must belong to SC category. Family annual income limit is up to ₹8,00,000. Must be enrolled in a recognized institution.",
                "amount": 50000.0,
                "deadline": default_deadline,
                "category_filter": "SC",
                "income_limit": 800000.0,
                "is_active": True
            },
            {
                "name": "Mahatma Jyotirao Phule Research Fellowship",
                "department": "Higher and Technical Education Department",
                "description": "Prestigious research fellowship for OBC researchers pursuing full-time M.Phil or Ph.D. degrees in Maharashtra state universities.",
                "eligibility_criteria": "Candidate must belong to OBC category. Post-graduate degree with minimum 55% marks. Family annual income up to ₹8,00,000.",
                "amount": 25000.0,
                "deadline": default_deadline,
                "category_filter": "OBC",
                "income_limit": 800000.0,
                "is_active": True
            },
            {
                "name": "Dr. Panjabrao Deshmukh Vasatigruh Nirvah Bhatta",
                "department": "Social Justice and Special Assistance Department",
                "description": "Hostel maintenance allowance for children of registered agricultural laborers and marginal landholders pursuing professional education.",
                "eligibility_criteria": "SC students enrolled in degree/diploma courses residing in college hostels or rented accommodation.",
                "amount": 30000.0,
                "deadline": default_deadline,
                "category_filter": "SC",
                "income_limit": None,
                "is_active": True
            },
            {
                "name": "Tuition Fee & Exam Fee for OBC Students",
                "department": "Other Backward Bahujan Welfare Department",
                "description": "Full or partial reimbursement of tuition and examination fees for OBC students in government-aided and private professional colleges.",
                "eligibility_criteria": "OBC category students with valid Caste and Non-Creamy Layer Certificate. Annual family income must not exceed ₹8,00,000.",
                "amount": 20000.0,
                "deadline": default_deadline,
                "category_filter": "OBC",
                "income_limit": 800000.0,
                "is_active": True
            },
            {
                "name": "Post Matric Scholarship for ST Students",
                "department": "Tribal Development Department",
                "description": "Comprehensive post-matriculation scholarship providing tuition fee waiver and maintenance stipend for Scheduled Tribe students.",
                "eligibility_criteria": "ST category students pursuing 11th, 12th, graduation, or post-graduation. Family income must not exceed ₹2,50,000 per annum.",
                "amount": 15000.0,
                "deadline": default_deadline,
                "category_filter": "ST",
                "income_limit": 250000.0,
                "is_active": True
            },
            {
                "name": "Merit-cum-Means Scholarship for Minorities",
                "department": "Minority Development Department",
                "description": "Merit and financial need-based financial aid for meritorious minority students (Muslim, Buddhist, Christian, Jain, Sikh, Parsi).",
                "eligibility_criteria": "Belong to a recognized religious minority in Maharashtra. Minimum 50% marks in qualifying exam. Annual family income up to ₹2,00,000.",
                "amount": 35000.0,
                "deadline": default_deadline,
                "category_filter": "All",
                "income_limit": 200000.0,
                "is_active": True
            }
        ]

        for s_data in scholarships_list:
            existing_scholarship = Scholarship.query.filter_by(name=s_data["name"]).first()
            if not existing_scholarship:
                scholarship = Scholarship(**s_data)
                db.session.add(scholarship)
                print(f"✓ Added Scholarship: {s_data['name']}")
            else:
                print(f"- Scholarship already exists: {s_data['name']}")

        db.session.commit()

        # Seed 1 sample application for demo student if none exists
        if demo_student:
            first_scholarship = Scholarship.query.filter_by(category_filter='OBC').first()
            if first_scholarship:
                existing_app = Application.query.filter_by(user_id=demo_student.id, scholarship_id=first_scholarship.id).first()
                if not existing_app:
                    sample_app = Application(
                        user_id=demo_student.id,
                        scholarship_id=first_scholarship.id,
                        status='under_review',
                        remarks='Documents verified by college clerk. Forwarded to Social Welfare Officer.'
                    )
                    db.session.add(sample_app)
                    db.session.commit()
                    print(f"✓ Created sample application for demo student on '{first_scholarship.name}'")

        print("\nSeed complete! All tables, accounts, and 6 scholarships are initialized successfully.")


if __name__ == '__main__':
    seed()
