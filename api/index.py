import os
import sys
import traceback

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from werkzeug.middleware.proxy_fix import ProxyFix


class VercelPathMiddleware:
    """
    Normalizes WSGI PATH_INFO & SCRIPT_NAME so that requests routed via Vercel
    serverless functions match Flask's route rules regardless of whether Vercel
    rewrote the path to /api/index.py, /api/index, or kept the original URL.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        environ["SCRIPT_NAME"] = ""
        path = environ.get("PATH_INFO", "")
        # If Vercel rewrites directly to the serverless function root
        if path in ("/api/index", "/api/index.py", "/api", ""):
            environ["PATH_INFO"] = "/"
        elif path.startswith("/api/index.py/"):
            environ["PATH_INFO"] = path[len("/api/index.py"):]
        elif path.startswith("/api/index/"):
            environ["PATH_INFO"] = path[len("/api/index"):]
        return self.wsgi_app(environ, start_response)


startup_error = None
try:
    from app import create_app
    app = create_app()

    # Wrap with ProxyFix for reverse proxy headers (host, proto, for)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    # Wrap with VercelPathMiddleware to eliminate 404s from Vercel function rewrites
    app.wsgi_app = VercelPathMiddleware(app.wsgi_app)

    @app.route("/api/index")
    @app.route("/api/index.py")
    def api_index_handler():
        from app.routes.home_routes import index
        return index()

    @app.route("/test-ping")
    def test_ping():
        return "TEST_PING_OK_200", 200

except Exception:
    startup_error = traceback.format_exc()
    from flask import Flask
    app = Flask(__name__)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_startup_error(path=""):
        return f"<h1>Startup Error</h1><pre>{startup_error}</pre>", 500



