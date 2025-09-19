import datetime

import pytest
from crud.webauthn import create_webauthncredential, get_webauthncredential, update_webauthncredential
from models.models import Player, WebAuthnCredential


@pytest.fixture
def dummy_player(db_session):
    player = Player(nick="dummy_player", password="dummy_pass", admin=False, judge=False)
    db_session.add(player)
    db_session.commit()
    return player


@pytest.fixture
def dummy_credential(dummy_player):
    cred = WebAuthnCredential(
        player_id=dummy_player.id,
        credential_id=b"dummy_credential_id",
        credential_public_key=b"dummy_public_key",
        current_sign_count=0,
        date_created=datetime.datetime.now(),
        date_last_used=datetime.datetime.now(),
    )
    return cred


def test_create_webauthncredential(db_session, dummy_credential):
    created = create_webauthncredential(db_session, dummy_credential)
    assert created.id is not None
    assert created.credential_id == b"dummy_credential_id"
    assert created.credential_public_key == b"dummy_public_key"
    assert created.current_sign_count == 0


def test_get_webauthncredential(db_session, dummy_credential):
    created = create_webauthncredential(db_session, dummy_credential)
    retrieved = get_webauthncredential(db_session, b"dummy_credential_id")
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.credential_id == b"dummy_credential_id"


def test_update_webauthncredential(db_session, dummy_credential):
    created = create_webauthncredential(db_session, dummy_credential)
    created.current_sign_count = 10

    updated = update_webauthncredential(db_session, created)
    retrieved = get_webauthncredential(db_session, b"dummy_credential_id")

    assert retrieved.current_sign_count == 10
