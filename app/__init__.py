from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("app.config.settings.Config")

    from app.routes.home_routes import home_bp
    from app.routes.history_routes import history_bp
    from app.routes.map_routes import map_bp
    from app.routes.timeline_routes import timeline_bp
    app.register_blueprint(home_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(timeline_bp)
    return app
