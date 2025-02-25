import base64
import datetime
from urllib.parse import urlparse

import webauthn
from config import Config
from crud.webauthn import create_webauthncredential, get_webauthncredential, update_webauthncredential
from extensions import db
from flask import request
from models.models import Player, WebAuthnCredential
from webauthn.helpers.structs import PublicKeyCredentialDescriptor, PublicKeyCredentialType, UserVerificationRequirement

REGISTRATION_CHALLENGES = {}


def _hostname():
    return str(urlparse(request.base_url).hostname)


def _origin():
    parsed = urlparse(request.base_url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _get_current_time():
    """Get current time in application's configured timezone"""
    config = Config()
    return datetime.datetime.now(config.get_timezone())


def prepare_credential_authentication(player: Player):
    """Generate the configuration needed by the client to start authenticating with an existing WebAuthn credential."""

    credentials = WebAuthnCredential.query.filter_by(player_id=player.id).all()

    allow_credentials = [
        PublicKeyCredentialDescriptor(id=cred.credential_id, type=PublicKeyCredentialType.PUBLIC_KEY)
        for cred in credentials
    ]

    public_credential_authentication_options = webauthn.generate_authentication_options(
        rp_id=_hostname(),
        allow_credentials=allow_credentials,
        user_verification=UserVerificationRequirement.DISCOURAGED,
    )

    to_session = public_credential_authentication_options.challenge

    return webauthn.options_to_json(public_credential_authentication_options), to_session


def prepare_credential_creation(player: Player):
    """Generate the configuration needed by the client to start registering a new WebAuthn credential."""

    public_credential_creation_options = webauthn.generate_registration_options(
        rp_id=_hostname(),
        rp_name="zmitac2",
        user_id=bytes(player.id),
        user_name=player.nick,
    )

    REGISTRATION_CHALLENGES[player.id] = {
        "challenge": public_credential_creation_options.challenge,
        "expires_at": _get_current_time() + datetime.timedelta(minutes=10),
    }

    return webauthn.options_to_json(public_credential_creation_options)


def _get_from_registration_challenges(player_id):
    challenge = REGISTRATION_CHALLENGES.get(player_id)
    if not challenge:
        return None

    expires_at = challenge.get("expires_at")
    now = _get_current_time()
    if expires_at < now:
        del REGISTRATION_CHALLENGES[player_id]
        return None

    return challenge["challenge"]


def verify_and_save_credential(player: Player, registration_credential):
    expected_challenge = _get_from_registration_challenges(player.id)

    auth_verification = webauthn.verify_registration_response(
        credential=registration_credential,
        expected_challenge=expected_challenge,
        expected_origin=_origin(),
        expected_rp_id=_hostname(),
    )

    credential = WebAuthnCredential(
        player_id=player.id,
        credential_public_key=auth_verification.credential_public_key,
        credential_id=auth_verification.credential_id,
        date_created=_get_current_time(),
        date_last_used=None,
    )

    create_webauthncredential(db.session, credential)

    return credential


def verify_credential(authentication_credential, session_login_challenge):
    """Verify WebAuthn authentication credential and return the player if valid."""

    credential_id = base64.urlsafe_b64decode(authentication_credential["id"] + "==")

    credential = get_webauthncredential(db.session, credential_id)

    if not credential or not session_login_challenge:
        return None

    auth_verification = webauthn.verify_authentication_response(
        credential=authentication_credential,
        expected_challenge=session_login_challenge,
        expected_origin=_origin(),
        expected_rp_id=_hostname(),
        credential_public_key=credential.credential_public_key,
        credential_current_sign_count=credential.current_sign_count,
    )

    credential.current_sign_count = auth_verification.new_sign_count
    credential.date_last_used = _get_current_time()

    update_webauthncredential(db.session, credential)

    return credential.player
