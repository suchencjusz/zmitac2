import datetime
from urllib.parse import urlparse

import webauthn
from extensions import db
from flask import request
from models.models import Player, WebAuthnCredential

REGISTRATION_CHALLENGES = {}


def _hostname():
    return str(urlparse(request.base_url).hostname)


def prepare_credential_creation(player: Player) -> tuple:
    """Generate the configuration needed by the client to start registering a new WebAuthn credential."""

    public_credential_creation_options = webauthn.generate_registration_options(
        rp_id=_hostname(),
        rp_name="zmitac2",
        user_id=bytes(player.id),
        user_name=player.nick,
    )

    REGISTRATION_CHALLENGES[player.id] = {
        "challenge": public_credential_creation_options.challenge,
        "expires_at": datetime.datetime.now() + datetime.timedelta(minutes=10),
    }

    return (webauthn.options_to_json(public_credential_creation_options), public_credential_creation_options)



def _get_from_registration_challenges(player_id):
    challenge = REGISTRATION_CHALLENGES.get(player_id)
    if not challenge:
        return None

    expires_at = challenge.get("expires_at")
    if expires_at < datetime.datetime.now():
        del REGISTRATION_CHALLENGES[player_id]
        return None

    return challenge["challenge"]


def verify_and_save_credential(player: Player, registration_credential):
    expected_challenge = _get_from_registration_challenges(player.id)

    auth_verification = webauthn.verify_registration_response(
        credential=registration_credential,
        expected_challenge=expected_challenge,
        # expected_origin=f"https://{_hostname()}", todo: fix this
        expected_origin=f"https://localhost:8001", 
        expected_rp_id=_hostname(),
    )

    credential = WebAuthnCredential(
        player_id=player.id,
        credential_public_key=auth_verification.credential_public_key,
        credential_id=auth_verification.credential_id,
    )

    db.session.add(credential)
    db.session.commit()
