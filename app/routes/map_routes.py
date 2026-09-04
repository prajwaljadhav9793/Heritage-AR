from flask import Blueprint, render_template, session

from app.services import profile_service

map_bp = Blueprint("map", __name__, url_prefix="/map")


@map_bp.get("/")
def heritage_map():
    user = session.get("user")
    wishlist_sites = []
    if user and user.get("uid"):
        prof = profile_service.get_user_profile(user["uid"], session_user=user)
        wishlist_sites = [item.get("site") for item in prof.get("wishlist", []) if item.get("site")]
        if prof.get("favoritePlace") and prof["favoritePlace"].get("site"):
            if prof["favoritePlace"]["site"] not in wishlist_sites:
                wishlist_sites.append(prof["favoritePlace"]["site"])

    return render_template(
        "map/heritage_map.html",
        user=user,
        wishlist_sites=wishlist_sites,
    )
