from flask import Blueprint, render_template
from flask_login import login_required
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()


match_bp = Blueprint("match", __name__)

@match_bp.route("/info", methods=["GET"])
def info():
    return render_template("match/info.html")

@match_bp.route("/test_match_info", methods=["GET"])
def test_match_info():
    return render_template("match/test_match_info.html")


