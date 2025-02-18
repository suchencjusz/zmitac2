import os

os.environ["TESTING"] = "True"

import pytest
from config import TestConfig
from extensions import db
from flask import Flask
from main import create_app
from models.models import Player
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

test_config = TestConfig()


@pytest.fixture(scope="session")
def engine() -> create_engine:
    engine = create_engine(test_config.DATABASE_URL)

    db.Model.metadata.drop_all(engine)
    db.Model.metadata.create_all(engine)

    yield engine

    db.Model.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def app() -> Flask:
    app = create_app(test_config)
    return app


@pytest.fixture(scope="function")
def test_client(app):
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture(scope="function")
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(app):
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture(scope="function")
def test_user(db_session):
    user = Player(nick="testuser", password=generate_password_hash("Password123!"), admin=False, judge=False)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def admin_user(db_session):
    admin = Player(nick="adminuser", password=generate_password_hash("AdminPass123!"), admin=True, judge=True)
    db_session.add(admin)
    db_session.commit()
    return admin
