import os

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

from datetime import datetime


from typing import Optional

db = SQLAlchemy()
login_manager = LoginManager()


def init_db(app) -> None:
    """Create all database tables."""

    from models.models import GameMode

    with app.app_context():
        db.create_all()

        # basic game modes
        if not GameMode.query.first():
            default_mode = GameMode(name="8-ball", description="Standardowy bilard")
            db.session.add(default_mode)
            db.session.commit()

        print("Database tables created.")

        ensure_admin_user()


def get_db() -> SQLAlchemy:
    """Get the database session."""

    return db.session


def ensure_admin_user():
    """Ensure that admin user exists, auto-create if not."""

    from crud.player import get_player_by_nick
    from models.models import Player

    admin_nick = os.environ.get("ADMIN_NICK", "admin")
    admin_pass = os.environ.get("ADMIN_PASSWORD", "admin")

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



def _pl_form(n: int, f1: str, f234: str, f_other: str) -> str:
    # 1 -> f1; 2-4 (z wykluczeniem 12-14) -> f234; reszta -> f_other
    if n == 1:
        return f1
    if 2 <= (n % 10) <= 4 and not 12 <= (n % 100) <= 14:
        return f234
    return f_other


def generate_elegant_datetime_ago(dt: Optional[datetime]) -> str:
    if not dt:
        return "-"

    now = datetime.now(dt.tzinfo) if getattr(dt, "tzinfo", None) else datetime.now()
    delta_seconds = int((now - dt).total_seconds())

    future = delta_seconds < 0
    delta_seconds = abs(delta_seconds)

    if delta_seconds < 5:
        return "przed chwilą" if not future else "za chwilę"

    days = delta_seconds // 86400
    rem = delta_seconds % 86400
    hours = rem // 3600
    rem %= 3600
    minutes = rem // 60
    seconds = rem % 60

    parts: list[str] = []

    if days:
        parts.append(f"{days} {'dzień' if days == 1 else 'dni'}")
    if hours and len(parts) < 2:
        parts.append(f"{hours} {_pl_form(hours, 'godzinę', 'godziny', 'godzin')}")
    if minutes and len(parts) < 2:
        parts.append(f"{minutes} {_pl_form(minutes, 'minutę', 'minuty', 'minut')}")
    if not parts:
        parts.append(f"{seconds} {_pl_form(seconds, 'sekundę', 'sekundy', 'sekund')}")

    text = ", ".join(parts)
    return f"za {text}" if future else f"{text} temu"