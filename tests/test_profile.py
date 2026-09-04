from app import create_app


def test_profile_redirects_unauthenticated():
    client = create_app().test_client()
    resp = client.get("/profile/")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_profile_renders_authenticated():
    client = create_app().test_client()
    with client.session_transaction() as sess:
        sess["user"] = {
            "uid": "user-test-123",
            "name": "Prajwal",
            "email": "prajwal@heritage.test",
            "member_since": "Aug 2025",
        }

    resp = client.get("/profile/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Prajwal" in html
    assert "prajwal@heritage.test" in html
    assert "Archival Passport" in html
    assert "Places Visited" in html
    assert "Wishlist" in html
    assert "Favorite Places" in html
    assert "AR Experiences" in html
    assert "Edit Profile" in html


def test_profile_update():
    client = create_app().test_client()
    with client.session_transaction() as sess:
        sess["user"] = {
            "uid": "user-update-123",
            "name": "Old Name",
            "email": "update@test.com",
        }

    resp = client.post(
        "/profile/update",
        data={"name": "New Explorer", "location": "Karnataka, India", "favorite_site": "Hampi"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess["user"]["name"] == "New Explorer"


def test_profile_favorite_update():
    client = create_app().test_client()
    with client.session_transaction() as sess:
        sess["user"] = {
            "uid": "user-fav-123",
            "name": "Prajwal",
            "email": "prajwal@test.com",
        }

    resp = client.post(
        "/profile/favorite",
        data={"site": "Konark Sun Temple"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Konark Sun Temple" in html


def test_profile_visited_add_and_remove():
    client = create_app().test_client()
    with client.session_transaction() as sess:
        sess["user"] = {
            "uid": "user-visit-123",
            "name": "Prajwal",
            "email": "prajwal@test.com",
        }

    # Add visited
    resp_add = client.post(
        "/profile/visited/add",
        data={"site": "Ajanta Caves", "date": "Oct 2025"},
        follow_redirects=True,
    )
    assert resp_add.status_code == 200
    assert "Ajanta Caves" in resp_add.get_data(as_text=True)

    # Remove visited
    resp_rem = client.post(
        "/profile/visited/remove",
        data={"site": "Ajanta Caves"},
        follow_redirects=True,
    )
    assert resp_rem.status_code == 200


def test_profile_wishlist_toggle_ajax():
    client = create_app().test_client()
    with client.session_transaction() as sess:
        sess["user"] = {
            "uid": "user-wish-123",
            "name": "Prajwal",
            "email": "prajwal@test.com",
        }

    # Toggle add
    resp = client.post(
        "/profile/wishlist/toggle",
        json={"site": "Martand Sun Temple", "location": "Jammu & Kashmir, India"},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True

    # Toggle remove
    resp2 = client.post(
        "/profile/wishlist/toggle",
        json={"site": "Martand Sun Temple"},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert data2["success"] is True
    assert data2["added"] is False


def test_profile_ar_visit_increment():
    client = create_app().test_client()
    with client.session_transaction() as sess:
        sess["user"] = {
            "uid": "user-ar-123",
            "name": "Prajwal",
            "email": "prajwal@test.com",
        }

    resp = client.post("/profile/ar-visit")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert "count" in data

