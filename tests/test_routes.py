from app import create_app


def test_home_route():
    client = create_app().test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"HeritageAR" in response.data
