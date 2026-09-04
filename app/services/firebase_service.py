
"""Firebase Authentication service for HeritageAR.

Setup (one time):
1. Go to https://console.firebase.google.com/ and create a project.
2. Project settings -> Service accounts -> "Generate new private key".
3. Save the downloaded JSON as  firebase-service-account.json  in the project
   root (next to app/). NEVER commit this file.
4. In the Firebase console open Authentication -> Sign-in method and enable
   "Email/Password".

The app reads the credentials from the FIREBASE_CREDENTIALS environment
variable (path to the JSON file). If it is not set, the file is looked up at
the project root automatically.

If Firebase is not configured, the app keeps working: auth functions return
(None, error message) and the routes show a friendly flash message instead of
crashing.
"""
import json
import os
from functools import lru_cache
from pathlib import Path

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import auth as firebase_auth, credentials, exceptions as firebase_exceptions

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CREDENTIALS_PATH = BASE_DIR / "firebase-service-account.json"


@lru_cache(maxsize=1)
def get_firebase_app():
    """Initialise the Firebase Admin SDK once. Returns None if not configured."""
    try:
        # Already initialised (e.g. app factory called twice in tests).
        return firebase_admin.get_app()
    except ValueError:
        pass

    credentials_path = os.getenv("FIREBASE_CREDENTIALS", str(DEFAULT_CREDENTIALS_PATH))
    credentials_file = Path(credentials_path)
    if not credentials_file.exists():
        return None

    try:
        cred = credentials.Certificate(str(credentials_file))
        return firebase_admin.initialize_app(cred)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"Firebase credentials invalid: {exc}")
        return None


def is_configured() -> bool:
    return get_firebase_app() is not None


def create_user(name: str, email: str, password: str):
    """Create a Firebase Auth user. Returns (user_record, None) or (None, error_message)."""
    app = get_firebase_app()
    if app is None:
        return None, (
            "Firebase is not configured yet. Add firebase-service-account.json "
            "to the project root (see app/services/firebase_service.py)."
        )
    try:
        user = firebase_auth.create_user(
            email=email,
            password=password,
            display_name=name,
            app=app,
        )
        return user, None
    except firebase_exceptions.EmailAlreadyExistsError:
        return None, "An account with this email already exists. Try signing in."
    except firebase_exceptions.InvalidEmailError:
        return None, "That email address does not look valid."
    except firebase_exceptions.WeakPasswordError:
        return None, "Please choose a stronger password (at least 6 characters)."
    except firebase_exceptions.FirebaseError as exc:
        code = getattr(exc, "code", "")
        if "email-already-exists" in code:
            return None, "An account with this email already exists. Try signing in."
        if "invalid-email" in code:
            return None, "That email address does not look valid."
        if "weak-password" in code:
            return None, "Please choose a stronger password (at least 6 characters)."
        print(f"Firebase create_user failed: {exc}")
        return None, "Could not create the account right now. Please try again."


def verify_user(email: str, password: str):
    """Verify a login against Firebase Auth.

    The Admin SDK cannot check passwords directly, so this uses the REST
    Identity Toolkit API with the project's Web API key.
    Returns (user_record, None) on success or (None, error_message).
    """
    app = get_firebase_app()
    if app is None:
        return None, (
            "Firebase is not configured yet. Add firebase-service-account.json "
            "to the project root (see app/services/firebase_service.py)."
        )

    api_key = os.getenv("FIREBASE_API_KEY", "")
    if not api_key:
        return None, (
            "FIREBASE_API_KEY is missing. Add it to your .env file "
            "(Firebase console -> Project settings -> General -> Web API key)."
        )

    import urllib.error
    import urllib.request

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = json.dumps({"email": email, "password": password, "returnSecureToken": True}).encode()
    request = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        try:
            message = json.loads(exc.read().decode()).get("error", {}).get("message", "")
        except Exception:
            message = ""
        if "EMAIL_NOT_FOUND" in message or "INVALID_PASSWORD" in message or "INVALID_LOGIN_CREDENTIALS" in message:
            return None, "Incorrect email or password."
        if "INVALID_EMAIL" in message:
            return None, "That email address does not look valid."
        if "TOO_MANY_ATTEMPTS" in message:
            return None, "Too many attempts. Please wait a moment and try again."
        print(f"Firebase login failed: {message or exc}")
        return None, "Could not sign in right now. Please try again."
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"Firebase unreachable: {exc}")
        return None, "Could not reach the authentication service. Please try again."

    try:
        user = firebase_auth.get_user_by_email(email, app=app)
    except firebase_exceptions.UserNotFoundError:
        user = None

    class _SessionUser:
        pass

    record = _SessionUser()
    record.uid = data.get("localId") or (user.uid if user else "")
    record.email = data.get("email", email)
    record.display_name = (user.display_name if user else None) or email.split("@")[0].replace(".", " ").title()
    return record, None
