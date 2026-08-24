from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("app.config.settings.Config")

    from app.routes.home_routes import home_bp
    app.register_blueprint(home_bp)
    return app
