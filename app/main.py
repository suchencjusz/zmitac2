import os

from config import Config, TestConfig
from extensions import db, ensure_admin_user, init_db, login_manager
from flask import Flask, flash, render_template
from flask_wtf.csrf import CSRFProtect
from models.models import Player


def create_app(config: Config) -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/static",
    )

    CSRFProtect(app)

    #
    # config & patch for tests
    #
    app.config.update(
        SECRET_KEY=config.SECRET_KEY.get_secret_value(),
        SQLALCHEMY_DATABASE_URI=config.DATABASE_URL,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        PERMANENT_SESSION_LIFETIME=config.get_session_lifetime(),
        DEBUG=config.DEBUG,
        WTF_CSRF_ENABLED=config.WTF_CSRF_ENABLED,
    )

    # Debug: print the final database URI used
    print("DEBUG: SQLALCHEMY_DATABASE_URI is set to:", app.config.get("SQLALCHEMY_DATABASE_URI"))

    #
    # basic flask and db
    #
    db.init_app(app)
    init_db(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Zaloguj się aby uzyskać dostęp."
    login_manager.login_message_category = "warning"

    #
    # flask-login user loader
    #
    @login_manager.user_loader
    def load_user(id):
        return Player.query.get(int(id))

    #
    # admin user - deafult
    #
    with app.app_context():
        ensure_admin_user()

    #
    # blueprints
    #
    from routes.admin_bp import admin_bp
    from routes.auth_bp import auth_bp
    from routes.info_bp import info_bp
    from routes.judge_bp import judge_bp
    from routes.match_bp import match_bp
    from routes.player_bp import player_bp
    from routes.webauthn_bp import webauthn_bp

    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(info_bp, url_prefix="/info")
    app.register_blueprint(judge_bp, url_prefix="/judge")
    app.register_blueprint(player_bp, url_prefix="/player")
    app.register_blueprint(match_bp, url_prefix="/match")
    app.register_blueprint(webauthn_bp, url_prefix="/webauthn")

    #
    # deafault routes
    #
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/test_flash")
    def test_flash():
        flash("Test flash message", "success")
        return render_template("index.html")

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app


app = create_app(TestConfig()) if os.getenv("TESTING") == "True" else create_app(Config())
