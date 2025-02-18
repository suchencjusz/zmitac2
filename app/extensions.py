import os

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()


def init_db(app) -> None:
    """Create all database tables."""

    with app.app_context():
        db.create_all()
        print("Database tables created.")


def get_db() -> SQLAlchemy:
    """Get the database session."""

    return db.session


def ensure_admin_user():
    """Ensure that admin user exists, auto-create if not."""

    admin_nick = os.environ.get("ADMIN_NICK")
    admin_pass = os.environ.get("ADMIN_PASSWORD", "admin")

    if not admin_nick:
        print("ADMIN_NICK environment variable not set, skipping admin user creation.")
        return

    from crud.player import get_player_by_nick
    from models.models import Player

    admin = get_player_by_nick(db.session, admin_nick)
    if not admin:
        admin = Player(
            nick=admin_nick,
            password=generate_password_hash(admin_pass),
            admin=True,
            judge=True,
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Created admin user: {admin_nick}")
    else:
        print("Admin user already exists.")
