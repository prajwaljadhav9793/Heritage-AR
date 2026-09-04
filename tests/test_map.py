from app import create_app
from app.services import profile_service


def test_heritage_map_renders():
    client = create_app().test_client()
    resp = client.get("/map/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    # Verify header & navigation
    assert "HeritageAR" in html
    assert "Explore" in html

    # Verify scrollable sidebar container
    assert "heritage-panel-list" in html
    assert "site-card-wrapper" in html

    # Verify favorite heart buttons are present
    assert "site-fav-btn" in html
    assert "data-wishlist" in html
    assert "map-toast" in html

    # Verify all heritage sites are in the list
    assert "Ajanta Caves" in html
    assert "Ellora Caves" in html
    assert "Raigad Fort" in html
    assert "Hampi" in html
    assert "Nalanda" in html
    assert "Konark Sun Temple" in html
    assert "Martand Sun Temple" in html
    assert "Meenakshi Temple" in html
    assert "Hoysaleshwara Temple" in html


def test_heritage_map_authenticated_with_wishlist():
    app = create_app()
    client = app.test_client()
    uid = "test-map-user-1"

    with client.session_transaction() as sess:
        sess["user"] = {
            "uid": uid,
            "name": "Arjun",
            "email": "arjun@example.com",
        }

    # Add Hampi to wishlist via AJAX endpoint
    client.post(
        "/profile/wishlist/toggle",
        json={"site": "Hampi", "location": "Karnataka, India"},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )

    resp = client.get("/map/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    # Active class should be applied for Hampi
    assert 'data-site="Hampi"' in html
    assert "is-active" in html


