"""Flask application factory for Campus Resource Hub v3."""
from __future__ import annotations

import os
from datetime import datetime

from flask import Flask, g
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect

from src.config import Config
from src.controllers import (
    auth_bp,
    resource_bp,
    dashboard_bp,
    booking_bp,
    message_bp,
    review_bp,
    admin_bp,
    site_bp,
)
from src.data_access.db import init_database, get_connection
from src.data_access.notification_dal import NotificationDAL
from src.data_access.user_dal import UserDAL

login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_object: type[Config] | None = None) -> Flask:
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_object or Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    csrf.init_app(app)

    with app.app_context():
        init_database(force=app.config.get('TESTING', False))

    @login_manager.user_loader
    def load_user(user_id):  # type: ignore[override]
        return UserDAL.get_user_by_id(int(user_id))

    app.register_blueprint(site_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(resource_bp, url_prefix='/resources')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(booking_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_layout_data():
        nav_notifications = []
        if current_user.is_authenticated:
            nav_notifications = NotificationDAL.list_for_user(current_user.user_id, limit=5)
        return {
            'current_year': datetime.utcnow().year,
            'app_name': 'Campus Resource Hub',
            'nav_notifications': nav_notifications,
        }

    @app.cli.command('init-db')
    def init_db_command():
        """CLI helper to rebuild the database schema."""
        init_database(force=True)
        print('Database initialized at', app.config['DATABASE_PATH'])

    @app.teardown_appcontext
    def close_connection(exception=None):
        conn = get_connection(close_only=True)
        if conn:
            conn.close()
            if hasattr(g, '_database'):
                g._database = None  # type: ignore[attr-defined]

    return app


if __name__ == '__main__':
    application = create_app()
    application.run(debug=True)
