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
