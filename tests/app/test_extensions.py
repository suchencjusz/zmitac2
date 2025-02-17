import os
import pytest
from flask import Flask
from werkzeug.security import check_password_hash

from extensions import db, login_manager, init_db, ensure_admin_user, get_db
from models.models import Player

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
    """Ensure that the database tables were created and are initially empty."""

    app = create_test_app()
    with app.app_context():
        players = Player.query.all()
        assert players == []

def test_get_db():
    """Verify that get_db returns a valid session and that we can add objects."""

    app = create_test_app()
    with app.app_context():
        session = get_db()
        player = Player(nick="test", password="dummy")

        session.add(player)
        session.commit()
        fetched = Player.query.filter_by(nick="test").first()

        assert fetched is not None
        assert fetched.nick == "test"

def test_ensure_admin_user(monkeypatch):
    """Ensure that ensure_admin_user creates the admin user when environment variables are set."""

    monkeypatch.setenv("ADMIN_NICK", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "adminpass")

    app = create_test_app()
    with app.app_context():
        admin = Player.query.filter_by(nick="admin").first()
        assert admin is None
        
        ensure_admin_user()
        
        admin = Player.query.filter_by(nick="admin").first()
        assert admin is not None
        assert check_password_hash(admin.password, "adminpass")
        assert admin.admin is True
        assert admin.judge is True