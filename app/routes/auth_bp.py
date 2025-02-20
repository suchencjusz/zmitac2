import datetime
from urllib.parse import urlparse

from flask_login import current_user

from crud.player import get_player, get_player_by_nick
from extensions import db
from flask import Blueprint, abort, flash, make_response, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from models.models import Player
from utils.auth import prepare_credential_creation, verify_and_save_credential
from webauthn.helpers.exceptions import InvalidRegistrationResponse
from webauthn.helpers.structs import RegistrationCredential
from werkzeug.security import check_password_hash, generate_password_hash

from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nick = request.form.get("nick")
        password = request.form.get("password")

        if not nick or not password:
            flash("Proszę wypełnić wszystkie pola!", "error")
            return render_template("auth/login.html")

        player = get_player_by_nick(db.session, nick)
        if player and check_password_hash(player.password, password):
            login_user(player)
            flash("Zalogowano pomyślnie!", "success")
            next_page = request.args.get("next", "")
            if next_page:
                next_page = next_page.replace("\\", "")
                if not urlparse(next_page).netloc and not urlparse(next_page).scheme:
                    return redirect(next_page)
            return redirect(url_for("index"))

        flash("Nieprawidłowy nick lub hasło!", "error")

    return render_template("auth/login.html")


@auth_bp.route("/add_webauthn", methods=["GET", "POST"])
@login_required
def add_webauth():
    return render_template("auth/add_webauthn.html")


@auth_bp.route("/add_webauthn_partial", methods=["GET", "POST"])
@login_required
def add_webauth_partial():

    pcco_json = prepare_credential_creation(current_user)

    session["registration_user_id"] = current_user.id
    
    res = make_response(
        render_template(
            "auth/_register_webauthn_fragment.html",
            public_credential_creation_options=pcco_json,
        )
    )
    session["registration_user_id"] = current_user.id

    return res

@auth_bp.route("/save_webauthn", methods=["POST"])
@login_required
def save_webauthn():
    player = current_user
    credential_data = request.get_json()

    if not credential_data:
        return make_response({"verified": False, "error": "No data provided"}, 400)

    try:
        verify_and_save_credential(
            player, 
            credential_data
        )
        
        session.pop("registration_user_id", None)
        
        return make_response({"verified": True}, 201)
    except InvalidRegistrationResponse as e:
        print(f"Registration error: {str(e)}")
        return make_response({"verified": False, "error": "error"}, 400)

# 1st to do: write verifiaction to check if this shit works (does it even? )

# @auth_bp.route("/save_webauthn", methods=["POST"])
# @login_required
# def save_webauthn():
#     player = current_user

#     if not request:
#         return make_response('{"verified": false, "error": "No data provided"}', 400)
    
#     print(request.get_json())

#     registration_credential = RegistrationCredential(request.get_json())

#     try:
#         verify_and_save_credential(player, registration_credential)
#         session["registration_user_id"] = None
#         res = make_response('{"verified": true}', 201)
#         res.set_cookie(
#             "user_id",
#             player.id,
#             httponly=True,
#             secure=True,
#             samesite="strict",
#             max_age=datetime.timedelta(days=30),
#         )
#         return res
#     except InvalidRegistrationResponse:
#         abort(make_response('{"verified": false}', 400))


# @auth_bp.route('/edit', methods=['GET', 'POST'])
# @login_required
# def edit():


@auth_bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        new_password2 = request.form.get("new_password2")

        if not old_password or not new_password or not new_password2:
            flash("Proszę wypełnić wszystkie pola!", "error")
            return render_template("auth/change_password.html")

        if not check_password_hash(current_user.password, old_password):
            flash("Nieprawidłowe stare hasło!", "error")
            return render_template("auth/change_password.html")

        if new_password != new_password2:
            flash("Nowe hasła nie są takie same!", "error")
            return render_template("auth/change_password.html")

        if len(new_password) < 10:
            flash("Nowe hasło musi mieć co najmniej 10 znaków!", "error")
            return render_template("auth/change_password.html")

        current_user.password = generate_password_hash(new_password)

        db.session.commit()
        flash("Hasło zostało zmienione!", "success")
        return redirect(url_for("index"))

    return render_template("auth/change_password.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Zostałeś wylogowany.", "info")
    return redirect(url_for("index"))
