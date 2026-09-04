from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from app.services import profile_service

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


def _current_user():
    user = session.get("user")
    if not user or not user.get("uid"):
        return None
    return user


def _is_ajax():
    return (
        request.is_json
        or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or "application/json" in request.headers.get("Accept", "")
    )


@profile_bp.get("/")
def view_profile():
    user = _current_user()
    if user is None:
        flash("Please sign in to view your Heritage profile.", "info")
        return redirect(url_for("auth.login"))

    profile = profile_service.get_user_profile(user["uid"], session_user=user)
    member_since = profile.get("memberSince") or user.get("member_since") or "Sep 2025"
    available_sites = profile_service.get_available_sites()

    return render_template(
        "profile/profile.html",
        profile=profile,
        user=user,
        member_since=member_since,
        available_sites=available_sites,
        firestore_ready=profile_service.is_firestore_ready(),
    )


@profile_bp.post("/update")
def update():
    user = _current_user()
    if user is None:
        if _is_ajax():
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    if request.is_json:
        data = request.get_json() or {}
        name = data.get("name", "").strip()
        location = data.get("location", "").strip()
        fav_site = data.get("favorite_site", "").strip()
    else:
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        fav_site = request.form.get("favorite_site", "").strip()

    updates = {}
    if name:
        updates["name"] = name
        session["user"]["name"] = name
    if location:
        updates["location"] = location

    if updates:
        profile_service.update_user_profile(user["uid"], **updates)

    if fav_site:
        profile_service.set_favorite_place(user["uid"], fav_site)

    if _is_ajax():
        updated = profile_service.get_user_profile(user["uid"], session_user=user)
        return jsonify({
            "success": True,
            "message": "Profile updated successfully.",
            "name": updated.get("name"),
            "location": updated.get("location"),
            "favoritePlace": updated.get("favoritePlace"),
        })

    flash("Profile updated successfully.", "success")
    return redirect(url_for("profile.view_profile"))


@profile_bp.post("/favorite")
def set_favorite():
    user = _current_user()
    if user is None:
        if _is_ajax():
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    if request.is_json:
        data = request.get_json() or {}
        site = data.get("site", "").strip()
        location = data.get("location", "").strip()
    else:
        site = request.form.get("site", "").strip()
        location = request.form.get("location", "").strip()

    if site:
        profile_service.set_favorite_place(user["uid"], site, location)

    if _is_ajax():
        prof = profile_service.get_user_profile(user["uid"], session_user=user)
        return jsonify({
            "success": True,
            "message": f"{site} set as favourite.",
            "favoritePlace": prof.get("favoritePlace", {}),
        })

    flash(f"{site} is now your favourite heritage site.", "success")
    return redirect(url_for("profile.view_profile"))


@profile_bp.post("/visited/add")
def add_visited():
    user = _current_user()
    if user is None:
        if _is_ajax():
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    if request.is_json:
        data = request.get_json() or {}
        site = data.get("site", "").strip()
        location = data.get("location", "").strip()
        date = data.get("date", "").strip()
    else:
        site = request.form.get("site", "").strip()
        location = request.form.get("location", "").strip()
        date = request.form.get("date", "").strip()

    if site:
        profile_service.add_visited_place(user["uid"], site, location, date=date)

    prof = profile_service.get_user_profile(user["uid"], session_user=user)
    visited_count = len(prof.get("visitedPlaces", []))

    if _is_ajax():
        return jsonify({
            "success": True,
            "message": f"{site} added to your visited places.",
            "count": visited_count,
            "visitedPlaces": prof.get("visitedPlaces", []),
        })

    flash(f"{site} added to your visited places.", "success")
    return redirect(url_for("profile.view_profile"))


@profile_bp.post("/visited/remove")
def remove_visited():
    user = _current_user()
    if user is None:
        if _is_ajax():
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    if request.is_json:
        data = request.get_json() or {}
        site = data.get("site", "").strip()
    else:
        site = request.form.get("site", "").strip()

    if site:
        profile_service.remove_visited_place(user["uid"], site)

    prof = profile_service.get_user_profile(user["uid"], session_user=user)
    visited_count = len(prof.get("visitedPlaces", []))

    if _is_ajax():
        return jsonify({
            "success": True,
            "message": f"{site} removed from your visited places.",
            "count": visited_count,
            "visitedPlaces": prof.get("visitedPlaces", []),
        })

    flash(f"{site} removed from your visited places.", "success")
    return redirect(url_for("profile.view_profile"))


@profile_bp.post("/wishlist/toggle")
def wishlist_toggle():
    user = _current_user()
    if user is None:
        if _is_ajax():
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    if request.is_json:
        data = request.get_json() or {}
        site = data.get("site", "").strip()
        location = data.get("location", "").strip()
    else:
        site = request.form.get("site", "").strip()
        location = request.form.get("location", "").strip()

    if site:
        added = profile_service.toggle_wishlist(user["uid"], site, location)
    else:
        added = False

    prof = profile_service.get_user_profile(user["uid"], session_user=user)
    count = len(prof.get("wishlist", []))

    if _is_ajax():
        return jsonify({
            "success": True,
            "added": added,
            "count": count,
            "message": f"{site} {'saved to' if added else 'removed from'} your wishlist.",
            "wishlist": prof.get("wishlist", []),
        })

    flash(
        f"{site} {'saved to' if added else 'removed from'} your wishlist.",
        "success",
    )
    return redirect(url_for("profile.view_profile"))


@profile_bp.post("/picture")
def upload_picture():
    user = _current_user()
    if user is None:
        if _is_ajax():
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    file = request.files.get("picture")
    if not file or not file.filename:
        if _is_ajax():
            return jsonify({"error": "Please choose an image file."}), 400
        flash("Choose an image first.", "error")
        return redirect(url_for("profile.view_profile"))

    filename = f"{user['uid']}.png"
    rel_path = profile_service.save_profile_picture(file, filename)
    if rel_path is None:
        if _is_ajax():
            return jsonify({"error": "Only PNG, JPG, or WEBP images are supported."}), 400
        flash("Only PNG, JPG, or WEBP images are supported.", "error")
        return redirect(url_for("profile.view_profile"))

    pic_url = url_for("static", filename=rel_path)
    profile_service.update_user_profile(user["uid"], profilePic=pic_url)

    if _is_ajax():
        return jsonify({
            "success": True,
            "message": "Profile picture updated.",
            "profilePic": pic_url,
        })

    flash("Profile picture updated.", "success")
    return redirect(url_for("profile.view_profile"))


@profile_bp.post("/ar-visit")
def record_ar_visit():
    user = _current_user()
    if user is None:
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    profile_service.increment_ar_experiences(user["uid"])
    prof = profile_service.get_user_profile(user["uid"], session_user=user)
    count = prof.get("stats", {}).get("arExperiences", 0)
    return jsonify({"ok": True, "count": count})
