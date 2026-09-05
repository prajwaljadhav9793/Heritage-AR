import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.middleware.proxy_fix import ProxyFix
from app import create_app

app = create_app()


class VercelPathMiddleware:
    """
    Normalizes WSGI PATH_INFO so that requests routed via Vercel serverless
    functions match Flask's route rules regardless of whether Vercel rewrote
    the path to /api/index.py, /api/index, or kept the original URL.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        # If Vercel rewrites directly to the serverless function root
        if path in ("/api/index", "/api/index.py", "/api", ""):
            environ["PATH_INFO"] = "/"
        elif path.startswith("/api/index.py/"):
            environ["PATH_INFO"] = path[len("/api/index.py"):]
        elif path.startswith("/api/index/"):
            environ["PATH_INFO"] = path[len("/api/index"):]
        return self.wsgi_app(environ, start_response)


# Wrap with ProxyFix for reverse proxy headers (host, proto, for)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
# Wrap with VercelPathMiddleware to eliminate 404s from Vercel function rewrites
app.wsgi_app = VercelPathMiddleware(app.wsgi_app)


@app.route("/test-ping")
def test_ping():
    return "TEST_PING_OK_200", 200


@app.errorhandler(404)
def debug_404(e):
    from flask import request
    return (
        f"DEBUG_VERCEL_REQUEST:\n"
        f"request.path: {request.path}\n"
        f"environ.PATH_INFO: {request.environ.get('PATH_INFO')}\n"
        f"environ.SCRIPT_NAME: {request.environ.get('SCRIPT_NAME')}\n"
        f"request.url: {request.url}\n"
        f"headers: {dict(request.headers)}\n"
    ), 200



