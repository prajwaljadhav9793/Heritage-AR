from app import create_app


def test_home_route():
    client = create_app().test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"HeritageAR" in response.data


def test_home_uses_ar_experience_nav_instead_of_then_vs_now():
    html = create_app().test_client().get("/").get_data(as_text=True)
    assert "AR Experience" in html
    assert 'href="/ar/"' in html
    assert "Then vs Now" not in html
    assert 'href="/history/then-vs-now"' not in html


def test_home_navbar_anonymous():
    client = create_app().test_client()
    html = client.get("/").get_data(as_text=True)
    assert html.count('href="/login"') == 1
    assert html.count('href="/register"') == 1
    assert "Sign out" not in html
    assert 'href="/profile/"' not in html


def test_home_navbar_authenticated():
    client = create_app().test_client()
    with client.session_transaction() as sess:
        sess["user"] = {"uid": "user-123", "name": "Prajwal", "email": "p@test.com"}
    html = client.get("/").get_data(as_text=True)
    assert 'href="/login"' not in html
    assert 'href="/register"' not in html
    assert "Sign out" in html
    assert 'href="/profile/"' in html
    assert "Prajwal" in html
