def test_auth_placeholder():
    assert True
from app import create_app
from unittest.mock import patch


class _Record:
    def __init__(self):
        self.uid = "test-uid"
        self.email = "test@example.com"
        self.display_name = "Test User"


def test_register_page_renders():
    client = create_app().test_client()
    resp = client.get("/register")
    assert resp.status_code == 200
    assert b"Create account" in resp.data


def test_login_page_renders():
    client = create_app().test_client()
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"Sign in" in resp.data


def test_register_success_sets_session():
    client = create_app().test_client()
    with patch("app.services.firebase_service.create_user") as mock:
        mock.return_value = (_Record(), None)
        resp = client.post(
            "/register",
            data={"name": "Test User", "email": "test@example.com", "password": "secret123"},
            follow_redirects=True,
        )
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess["user"]["email"] == "test@example.com"
        assert sess["user"]["uid"] == "test-uid"


def test_register_validation_error():
    client = create_app().test_client()
    resp = client.post("/register", data={"name": "", "email": "bad", "password": "123"})
    assert resp.status_code == 400


def test_login_success_sets_session():
    client = create_app().test_client()
    with patch("app.services.firebase_service.verify_user") as mock:
        mock.return_value = (_Record(), None)
        resp = client.post(
            "/login",
            data={"email": "test@example.com", "password": "secret123"},
            follow_redirects=True,
        )
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess["user"]["email"] == "test@example.com"


def test_login_invalid_credentials():
    client = create_app().test_client()
    with patch("app.services.firebase_service.verify_user") as mock:
        mock.return_value = (None, "Incorrect email or password.")
        resp = client.post("/login", data={"email": "test@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_logout_clears_session():
    client = create_app().test_client()
    with client.session_transaction() as sess:
        sess["user"] = {"email": "a@b.c", "name": "A", "uid": "x"}
    resp = client.get("/logout", follow_redirects=True)
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert "user" not in sess
