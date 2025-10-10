from extensions import db, ensure_admin_user, get_db, init_db, login_manager
from flask import Flask
from models.models import GameMode, Player
from werkzeug.security import check_password_hash


def create_test_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="testsecret",
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)
    login_manager.init_app(app)
    with app.app_context():
        init_db(app)
    return app


def test_db_initialization():
    """Test that init_db creates tables, default game mode, and admin user."""
    app = create_test_app()
    with app.app_context():
        # Check that admin was created automatically
        admin = Player.query.filter_by(nick="admin").first()
        assert admin is not None
        assert admin.admin is True
        assert admin.judge is True
        
        # Check that default game mode was created
        gamemode = GameMode.query.filter_by(name="8-ball").first()
        assert gamemode is not None
        assert gamemode.description == "Standardowy bilard"


def test_get_db():
    app = create_test_app()
    with app.app_context():
        session = get_db()
        player = Player(nick="test", password="dummy")

        session.add(player)
        session.commit()
        fetched = Player.query.filter_by(nick="test").first()

        assert fetched is not None
        assert fetched.nick == "test"


def test_ensure_admin_user_idempotent(monkeypatch):
    """Test that calling ensure_admin_user multiple times doesn't create duplicates."""
    monkeypatch.setenv("ADMIN_NICK", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "adminpass")

    app = create_test_app()
    with app.app_context():
        count_before = Player.query.filter_by(nick="admin").count()
        assert count_before == 1
        
        ensure_admin_user()
        
        count_after = Player.query.filter_by(nick="admin").count()
        assert count_after == 1
        
        admin = Player.query.filter_by(nick="admin").first()
        assert admin.admin is True
        assert admin.judge is True
