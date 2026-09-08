import os
from datetime import datetime
from flask import Flask, send_from_directory, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from models import db, User
from routes.auth import auth_bp
from routes.student import student_bp
from routes.admin import admin_bp


def create_app():
    """Application factory for the MahaDBT Scholarship Tracker Flask application."""
    app = Flask(__name__)

    # Base directories
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(basedir, 'instance')
    os.makedirs(instance_dir, exist_ok=True)

    upload_dir = os.path.join(basedir, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    # Core Configurations
    db_path = os.path.join(instance_dir, 'mahadbt.db').replace('\\', '/')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mahadbt-tracker-super-secret-key-2026')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = upload_dir
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload limit

    # Initialize Extensions
    db.init_app(app)

    csrf = CSRFProtect()
    csrf.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Static uploads handler
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    # Template context processors
    @app.context_processor
    def inject_globals():
        return {
            'now': datetime.utcnow(),
            'current_year': datetime.utcnow().year
        }

    # HTTP Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def file_too_large(error):
        return "File is too large. Maximum allowed size is 16MB.", 413

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Ensure tables are created
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
