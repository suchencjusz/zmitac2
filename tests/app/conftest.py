import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from extensions import db

TEST_DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5432/zmitac_test"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL)
    db.Model.metadata.create_all(engine)
    yield engine
    db.Model.metadata.drop_all(engine)

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