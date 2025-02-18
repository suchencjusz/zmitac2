from datetime import datetime, timezone
import pytest
from crud.webauthn import create_webauthn_credential, get_player_webauthn_credentials
from crud.player import create_player
from schemas.schemas import WebauthnCredentialCreate, PlayerCreate
from models.models import WebauthnCredential

def test_create_webauthn_credential(db_session):
    # Create a test player first
    player = create_player(
        db_session, 
        PlayerCreate(nick="test_user", password="test123")
    )
    
    # Create test credential
    credential_data = WebauthnCredentialCreate(
        player_id=player.id,
        public_key=b"test_public_key",
        sign_count=0,
        name="Test Device"
    )
    
    credential = create_webauthn_credential(db_session, credential_data)
    
    assert credential.id is not None
    assert credential.player_id == player.id
    assert credential.public_key == b"test_public_key"
    assert credential.sign_count == 0
    assert credential.name == "Test Device"
    assert isinstance(credential.created_at, datetime)
    assert isinstance(credential.last_used_at, datetime)

def test_get_player_webauthn_credentials(db_session):
    # Create a test player
    player = create_player(
        db_session, 
        PlayerCreate(nick="test_user", password="test123")
    )
    
    # Create multiple credentials
    cred1 = WebauthnCredentialCreate(
        player_id=player.id,
        public_key=b"key1",
        sign_count=0,
        name="Device 1"
    )
    
    cred2 = WebauthnCredentialCreate(
        player_id=player.id,
        public_key=b"key2", 
        sign_count=0,
        name="Device 2"
    )
    
    create_webauthn_credential(db_session, cred1)
    create_webauthn_credential(db_session, cred2)
    
    credentials = get_player_webauthn_credentials(db_session, player.id)
    
    assert len(credentials) == 2
    assert {c.name for c in credentials} == {"Device 1", "Device 2"}