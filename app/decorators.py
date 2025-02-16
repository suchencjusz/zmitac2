from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user, login_required


def admin_required(func):
    @wraps(func)
    @login_required
    def decorated_view(*args, **kwargs):
        if not current_user.admin:
            flash("Wymagane uprawnienia administratora.", "error")
            return redirect(url_for("index"))
        return func(*args, **kwargs)

    return decorated_view


def judge_required(func):
    @wraps(func)
    @login_required
    def decorated_view(*args, **kwargs):
        if not (current_user.judge or current_user.admin):
            flash("Wymagane uprawnienia sędziego.", "error")
            return redirect(url_for("index"))
        return func(*args, **kwargs)

    return decorated_view
