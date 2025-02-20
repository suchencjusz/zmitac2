import datetime
from urllib.parse import urlparse

from crud.player import get_player, get_player_by_nick
from extensions import db
from flask import (Blueprint, abort, flash, make_response, redirect,
                   render_template, request, session, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from models.models import Player, WebAuthnCredential
from utils.auth import prepare_credential_creation, verify_and_save_credential
from webauthn.helpers.exceptions import InvalidRegistrationResponse
from webauthn.helpers.structs import RegistrationCredential
from werkzeug.security import check_password_hash, generate_password_hash

webauthn_bp = Blueprint("webauthn", __name__)


# @webauthn_bp.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         nick = request.form.get("nick")

#         pass


#     return render_template("auth/_login_webauthn_fragment.html.html")


@webauthn_bp.route("/add_webauthn", methods=["GET", "POST"])
@login_required
def add_webauthn():
    return render_template("webauthn/add_webauthn.html")


@webauthn_bp.route("/add_webauthn_partial", methods=["GET", "POST"])
@login_required
def add_webauthn_partial():

    pcco_json = prepare_credential_creation(current_user)

    session["registration_user_id"] = current_user.id

    res = make_response(
        render_template(
            "webauthn/_register_webauthn_fragment.html",
            public_credential_creation_options=pcco_json,
        )
    )
    session["registration_user_id"] = current_user.id

    return res


@webauthn_bp.route("/save_webauthn", methods=["POST"])
@login_required
def save_webauthn():
    player = current_user
    credential_data = request.get_json()

    if not credential_data:
        return make_response({"verified": False, "error": "No data provided"}, 400)

    try:
        verify_and_save_credential(player, credential_data)

        session.pop("registration_user_id", None)

        return make_response({"verified": True}, 201)
    except InvalidRegistrationResponse as e:
        print(f"Registration error: {str(e)}")
        return make_response({"verified": False, "error": "error"}, 400)


@webauthn_bp.route("/actions")
@login_required
def actions():
    credentials = WebAuthnCredential.query.filter_by(player_id=current_user.id).all()  # todo: rewrite to crud
    return render_template("webauthn/actions.html", credentials=credentials)


@webauthn_bp.route("/remove_credential/<int:credential_id>", methods=["POST"])
@login_required
def remove_credential(credential_id):
    credential = WebAuthnCredential.query.filter_by(  # todo: rewrite to crud
        id=credential_id, player_id=current_user.id
    ).first_or_404()

    db.session.delete(credential)
    db.session.commit()
    flash("Klucz został usunięty.")

    return redirect(url_for("webauthn.actions"))
