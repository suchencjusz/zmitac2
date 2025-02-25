import base64
import datetime
from unittest.mock import MagicMock, patch

import pytest
from config import Config
from extensions import db
from flask import Flask
from models.models import Player, WebAuthnCredential
from utils.auth import (
    REGISTRATION_CHALLENGES,
    _get_current_time,
    _get_from_registration_challenges,
    _hostname,
    _origin,
    prepare_credential_authentication,
    prepare_credential_creation,
    verify_and_save_credential,
    verify_credential,
)
from webauthn.helpers.exceptions import InvalidRegistrationResponse


@pytest.fixture
def app():
    """Create a Flask application configured for testing."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    return app


@pytest.fixture
def app_context(app):
    """Create an application context for testing."""
    with app.app_context():
        yield


@pytest.fixture
def request_context(app):
    """Create a request context for testing URL functions."""
    with app.test_request_context("https://example.com/test"):
        yield


@pytest.fixture
def test_player(db_session):
    """Create a test player with WebAuthn credentials."""
    player = Player(nick="webauthn_test_user", password="password123", admin=False, judge=False)
    db_session.add(player)
    db_session.commit()

    credential = WebAuthnCredential(
        player_id=player.id,
        credential_id=b"test_credential_id",
        credential_public_key=b"test_public_key",
        current_sign_count=5,
        date_created=datetime.datetime.now(),
        date_last_used=datetime.datetime.now(),
    )
    db_session.add(credential)
    db_session.commit()

    return player


def test_hostname(request_context):
    """Test that _hostname extracts the hostname correctly."""
    assert _hostname() == "example.com"


def test_origin(request_context):
    """Test that _origin returns the full origin URL."""
    assert _origin() == "https://example.com"


def test_get_current_time():
    """Test that _get_current_time returns a datetime in the configured timezone."""
    with patch.object(Config, "get_timezone", return_value=datetime.timezone.utc):
        current_time = _get_current_time()
        assert isinstance(current_time, datetime.datetime)

        now = datetime.datetime.now(datetime.timezone.utc)
        assert abs((now - current_time).total_seconds()) < 10


def test_prepare_credential_authentication(app_context, request_context):
    """Test that prepare_credential_authentication returns options JSON and session challenge."""

    test_player = MagicMock()
    test_player.id = 123

    with patch("utils.auth.WebAuthnCredential") as MockCredModel:
        mock_cred = MagicMock()
        mock_cred.credential_id = b"test_credential_id"
        MockCredModel.query.filter_by.return_value.all.return_value = [mock_cred]

        with patch("webauthn.generate_authentication_options") as mock_gen_auth_options:
            mock_options = MagicMock()
            mock_options.challenge = b"test_challenge"
            mock_gen_auth_options.return_value = mock_options

            with patch("webauthn.options_to_json", return_value='{"test": "json"}'):
                options_json, challenge = prepare_credential_authentication(test_player)

                assert options_json == '{"test": "json"}'
                assert challenge == b"test_challenge"

                mock_gen_auth_options.assert_called_once()
                call_kwargs = mock_gen_auth_options.call_args.kwargs
                assert call_kwargs["rp_id"] == "example.com"
                assert len(call_kwargs["allow_credentials"]) == 1


def test_prepare_credential_creation(request_context):
    """Test that prepare_credential_creation stores challenge and returns options."""

    test_player = MagicMock()
    test_player.id = 123
    test_player.nick = "test_user"

    with patch("webauthn.generate_registration_options") as mock_gen_reg_options:
        mock_options = MagicMock()
        mock_options.challenge = b"test_registration_challenge"
        mock_gen_reg_options.return_value = mock_options

        with patch("webauthn.options_to_json", return_value='{"registration": "options"}'):
            REGISTRATION_CHALLENGES.clear()

            options_json = prepare_credential_creation(test_player)

            assert options_json == '{"registration": "options"}'

            assert test_player.id in REGISTRATION_CHALLENGES
            assert REGISTRATION_CHALLENGES[test_player.id]["challenge"] == b"test_registration_challenge"

            expires_at = REGISTRATION_CHALLENGES[test_player.id]["expires_at"]
            now = _get_current_time()
            time_diff = (expires_at - now).total_seconds()
            assert 500 < time_diff < 700  # ~10 minutes


def test_get_from_registration_challenges():
    """Test retrieving challenges from the registration challenges store."""
    REGISTRATION_CHALLENGES.clear()

    now = _get_current_time()
    valid_future = now + datetime.timedelta(minutes=5)
    expired_past = now - datetime.timedelta(minutes=5)

    REGISTRATION_CHALLENGES[1] = {"challenge": b"valid", "expires_at": valid_future}
    REGISTRATION_CHALLENGES[2] = {"challenge": b"expired", "expires_at": expired_past}
    REGISTRATION_CHALLENGES[3] = {"challenge": None, "expires_at": valid_future}

    assert _get_from_registration_challenges(1) == b"valid"

    assert _get_from_registration_challenges(2) is None
    assert 2 not in REGISTRATION_CHALLENGES

    assert _get_from_registration_challenges(999) is None


# Fix both authentication tests with proper mocking

# def test_verify_and_save_credential(app_context):
#     """Test that verify_and_save_credential validates and saves credentials."""

#     test_player = MagicMock()
#     test_player.id = 123

#     mock_saved_credential = MagicMock()

#     with patch("utils.auth._get_from_registration_challenges") as mock_get_challenge, \
#          patch("webauthn.verify_registration_response") as mock_verify, \
#          patch("utils.auth.WebAuthnCredential") as MockCredModel, \
#          patch("crud.webauthn.create_webauthncredential", return_value=mock_saved_credential) as mock_create_cred, \
#          patch("utils.auth.db"):

#         mock_get_challenge.return_value = b"valid_challenge"

#         mock_verification = MagicMock()
#         mock_verification.credential_id = b"new_credential_id"
#         mock_verification.credential_public_key = b"new_credential_public_key"
#         mock_verify.return_value = mock_verification

#         with patch("utils.auth._hostname", return_value="example.com"), \
#              patch("utils.auth._origin", return_value="https://example.com"):

#             mock_reg_credential = {"id": "test_id", "rawId": "test_raw_id"}
#             result = verify_and_save_credential(test_player, mock_reg_credential)

#             mock_verify.assert_called_once()
#             call_args = mock_verify.call_args[1]
#             assert call_args["credential"] == mock_reg_credential
#             assert call_args["expected_challenge"] == b"valid_challenge"
#             assert call_args["expected_origin"] == "https://example.com"
#             assert call_args["expected_rp_id"] == "example.com"

#             MockCredModel.assert_called_once()
#             assert result == mock_saved_credential


# def test_verify_credential(app_context):
#     """Test that verify_credential validates credentials and returns the player."""
#     auth_credential = {"id": "dGVzdF9jcmVkZW50aWFsX2lk"}
#     session_challenge = b"test_challenge"

#     with patch("crud.webauthn.get_webauthncredential") as mock_get_cred, \
#          patch("webauthn.verify_authentication_response") as mock_verify_auth, \
#          patch("utils.auth._hostname", return_value="example.com"), \
#          patch("utils.auth._origin", return_value="https://example.com"), \
#          patch("utils.auth._get_current_time"), \
#          patch("crud.webauthn.update_webauthncredential") as mock_update, \
#          patch("utils.auth.db.session.query") as mock_query:

#         mock_credential = MagicMock()
#         mock_credential.credential_public_key = b"test_public_key"
#         mock_credential.credential_id = base64.urlsafe_b64decode("dGVzdF9jcmVkZW50aWFsX2lk" + "==")
#         mock_credential.current_sign_count = 10
#         mock_credential.player = MagicMock(id=123, nick="test_user")

#         mock_get_cred.return_value = mock_credential

#         mock_filter = mock_query.return_value.filter.return_value
#         mock_filter.first.return_value = mock_credential.player

#         mock_auth_verification = MagicMock()
#         mock_auth_verification.new_sign_count = 11
#         mock_verify_auth.return_value = mock_auth_verification

#         returned_player = verify_credential(auth_credential, session_challenge)

#         assert returned_player.id == mock_credential.player.id

#         mock_verify_auth.assert_called_once()
#         call_args = mock_verify_auth.call_args
#         assert call_args[1]["expected_challenge"] == session_challenge
#         assert call_args[1]["expected_origin"] == "https://example.com"
#         assert call_args[1]["expected_rp_id"] == "example.com"

#         mock_update.assert_called_once()
#         assert mock_credential.current_sign_count == 11
