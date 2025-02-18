from flask import Blueprint, render_template
from flask_login import login_required

info_bp = Blueprint("info", __name__)


@info_bp.route("/actions", methods=["GET"])
@login_required
def actions():
    return render_template("info/actions.html")


@info_bp.route("/about", methods=["GET"])
def about():
    return render_template("info/about.html")


@info_bp.route("/rules", methods=["GET"])
def rules():
    return render_template("info/rules.html")
