"""Firestore-backed user profile data for HeritageAR.

users/{uid}
  - name, email, profilePic, location, memberSince
  - favoritePlace -> {site, location, image, description}
  - visitedPlaces -> [{site, location, image, date, description}]
  - wishlist      -> [{site, location, image, description}]
  - stats         -> {arExperiences: int}

Degrades gracefully to an in-memory fallback when Firestore is unavailable or disabled.
"""
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from firebase_admin import firestore

from app.services import firebase_service

HERITAGE_IMAGES = {
    "Raigad Fort": "images/heritage/raigad-hero.jpg",
    "Hampi": "images/timeline/virupaksha.jpg",
    "Konark Sun Temple": "images/timeline/konark-01.jpg",
    "Meenakshi Temple": "images/timeline/meenakshi-gopuram.jpg",
    "Nalanda": "images/heritage/nalanda-ruins.jpg",
    "Khajuraho": "images/timeline/halebidu-temple-exterior.jpg",
    "Martand Sun Temple": "images/timeline/martand-01.png",
    "Ajanta Caves": "images/heritage/discover-fort.jpg",
    "Ellora Caves": "images/historical/now-fort.jpg",
    "Halebidu": "images/timeline/halebidu-entrance.jpg",
}

SITE_LOCATIONS = {
    "Raigad Fort": "Maharashtra, India",
    "Hampi": "Karnataka, India",
    "Konark Sun Temple": "Odisha, India",
    "Meenakshi Temple": "Tamil Nadu, India",
    "Nalanda": "Bihar, India",
    "Khajuraho": "Madhya Pradesh, India",
    "Martand Sun Temple": "Jammu & Kashmir, India",
    "Ajanta Caves": "Maharashtra, India",
    "Ellora Caves": "Maharashtra, India",
    "Halebidu": "Karnataka, India",
}

SITE_DESCRIPTIONS = {
    "Raigad Fort": "The formidable mountain capital where Chhatrapati Shivaji Maharaj was crowned and the Maratha sovereign kingdom rose in 1674.",
    "Hampi": "The ruined capital of the Vijayanagara Empire, scattered with stone chariots, monumental shrines, and royal pavilions among boulder hills.",
    "Konark Sun Temple": "A 13th-century colossal stone chariot dedicated to Surya, with 24 intricately carved stone wheels and mythical war horses.",
    "Meenakshi Temple": "The historic temple city of Madurai, adorned with towering 14-story gopurams alive with thousands of vibrant mythological sculptures.",
    "Nalanda": "The ancient international university and Buddhist monastery that hosted ten thousand scholars and pilgrims across Asia for 700 years.",
    "Khajuraho": "A UNESCO World Heritage complex of Nagara-style sandstone temples celebrated for intricate architectural finesse and celestial carvings.",
    "Martand Sun Temple": "The majestic 8th-century Kashmiri stone sanctuary built by King Lalitaditya Muktapida atop the Anantnag plateau.",
    "Ajanta Caves": "Masterpiece rock-cut Buddhist sanctuaries carved into a dramatic horseshoe gorge, preserving 2,000-year-old murals and sculptures.",
    "Ellora Caves": "A stunning rock-cut cave complex featuring the Kailash temple, carved out of a single monolithic basalt cliff face.",
    "Halebidu": "The 12th-century seat of the Hoysala Empire, renowned for the star-shaped Hoysaleshwara temple carved with exquisite chloritic schist friezes.",
}

# In-memory fallback for local environments or when Firestore is offline
_LOCAL_PROFILES = {}
_FIRESTORE_DISABLED = False


def _static_image(site_name):
    from flask import url_for

    filename = HERITAGE_IMAGES.get(site_name)
    return url_for("static", filename=filename) if filename else None


def _site_record(site, location="", image=None, date=None, **extra):
    loc = location or SITE_LOCATIONS.get(site, "India")
    img = image or _static_image(site) or ""
    desc = SITE_DESCRIPTIONS.get(site, "An ancient architectural wonder of Indian heritage.")
    record = {
        "site": site,
        "location": loc,
        "image": img,
        "description": desc,
    }
    if date:
        record["date"] = date
    record.update(extra)
    return record


def get_available_sites():
    """Return all curated heritage sites with metadata."""
    sites = []
    for site, loc in SITE_LOCATIONS.items():
        sites.append({
            "name": site,
            "location": loc,
            "description": SITE_DESCRIPTIONS.get(site, ""),
            "image": _static_image(site),
        })
    return sites


@lru_cache(maxsize=1)
def get_firestore_client():
    global _FIRESTORE_DISABLED
    if _FIRESTORE_DISABLED:
        return None
    app = firebase_service.get_firebase_app()
    if app is None:
        return None
    try:
        return firestore.client(app=app)
    except Exception as exc:
        print(f"Firestore client init failed: {exc}")
        _FIRESTORE_DISABLED = True
        return None


def is_firestore_ready() -> bool:
    return not _FIRESTORE_DISABLED and get_firestore_client() is not None


def _users_collection():
    global _FIRESTORE_DISABLED
    if _FIRESTORE_DISABLED:
        return None
    client = get_firestore_client()
    return client.collection("users") if client else None


def _get_default_profile(session_user: dict = None) -> dict:
    session_user = session_user or {}
    return {
        "name": session_user.get("name") or "Heritage Explorer",
        "email": session_user.get("email") or "",
        "profilePic": "",
        "location": "Maharashtra, India",
        "favoritePlace": _site_record(
            "Raigad Fort",
            "Maharashtra, India",
            description=SITE_DESCRIPTIONS["Raigad Fort"]
        ),
        "visitedPlaces": [
            _site_record("Raigad Fort", "Maharashtra, India", date="Nov 2025"),
            _site_record("Hampi", "Karnataka, India", date="Jan 2026"),
        ],
        "wishlist": [
            _site_record("Konark Sun Temple", "Odisha, India"),
            _site_record("Meenakshi Temple", "Tamil Nadu, India"),
            _site_record("Ajanta Caves", "Maharashtra, India"),
        ],
        "stats": {"arExperiences": 3},
        "memberSince": session_user.get("member_since") or "Sep 2025",
    }


def get_user_profile(uid: str, session_user: dict = None) -> dict:
    global _FIRESTORE_DISABLED
    default = _get_default_profile(session_user)
    users = _users_collection()
    if users is None:
        if uid not in _LOCAL_PROFILES:
            _LOCAL_PROFILES[uid] = default
        if session_user:
            if session_user.get("name"):
                _LOCAL_PROFILES[uid]["name"] = session_user["name"]
            if session_user.get("email"):
                _LOCAL_PROFILES[uid]["email"] = session_user["email"]
        return _LOCAL_PROFILES[uid]

    try:
        doc = users.document(uid).get()
        if not doc.exists:
            users.document(uid).set(default)
            return default
        data = doc.to_dict() or {}
        merged = {**default, **data}
        if session_user and not merged.get("name") and session_user.get("name"):
            merged["name"] = session_user["name"]
        if session_user and not merged.get("email") and session_user.get("email"):
            merged["email"] = session_user["email"]
        return merged
    except Exception as exc:
        if "SERVICE_DISABLED" in str(exc) or "not been used in project" in str(exc):
            _FIRESTORE_DISABLED = True
        print(f"Using local profile fallback: {exc}")
        if uid not in _LOCAL_PROFILES:
            _LOCAL_PROFILES[uid] = default
        return _LOCAL_PROFILES[uid]


def get_member_since(uid: str) -> str:
    profile = get_user_profile(uid)
    return profile.get("memberSince", "Sep 2025")


def update_user_profile(uid: str, **fields) -> None:
    global _FIRESTORE_DISABLED
    users = _users_collection()
    if users is not None:
        try:
            users.document(uid).set(fields, merge=True)
        except Exception as exc:
            if "SERVICE_DISABLED" in str(exc) or "not been used in project" in str(exc):
                _FIRESTORE_DISABLED = True
            print(f"Firestore update error: {exc}")

    if uid in _LOCAL_PROFILES:
        _LOCAL_PROFILES[uid].update(fields)
    else:
        prof = _get_default_profile()
        prof.update(fields)
        _LOCAL_PROFILES[uid] = prof


def add_visited_place(uid: str, site: str, location: str = "", date: str = "") -> None:
    global _FIRESTORE_DISABLED
    if not site:
        return
    if not date:
        date = datetime.now().strftime("%b %Y")
    record = _site_record(site, location, date=date)

    users = _users_collection()
    if users is not None:
        try:
            profile = get_user_profile(uid)
            if not any(p.get("site") == site for p in profile.get("visitedPlaces", [])):
                users.document(uid).set(
                    {"visitedPlaces": firestore.ArrayUnion([record])},
                    merge=True,
                )
        except Exception as exc:
            if "SERVICE_DISABLED" in str(exc) or "not been used in project" in str(exc):
                _FIRESTORE_DISABLED = True
            print(f"Firestore add_visited error: {exc}")

    prof = get_user_profile(uid)
    visited = prof.get("visitedPlaces", [])
    if not any(p.get("site") == site for p in visited):
        visited.append(record)
        prof["visitedPlaces"] = visited
        _LOCAL_PROFILES[uid] = prof


def remove_visited_place(uid: str, site: str) -> None:
    global _FIRESTORE_DISABLED
    if not site:
        return
    users = _users_collection()
    if users is not None:
        try:
            profile = get_user_profile(uid)
            remaining = [p for p in profile.get("visitedPlaces", []) if p.get("site") != site]
            users.document(uid).set({"visitedPlaces": remaining}, merge=True)
        except Exception as exc:
            if "SERVICE_DISABLED" in str(exc) or "not been used in project" in str(exc):
                _FIRESTORE_DISABLED = True
            print(f"Firestore remove_visited error: {exc}")

    prof = get_user_profile(uid)
    remaining = [p for p in prof.get("visitedPlaces", []) if p.get("site") != site]
    prof["visitedPlaces"] = remaining
    _LOCAL_PROFILES[uid] = prof


def toggle_wishlist(uid: str, site: str, location: str = "") -> bool:
    global _FIRESTORE_DISABLED
    if not site:
        return False
    prof = get_user_profile(uid)
    wishlist = prof.get("wishlist", [])
    is_saved = any(entry.get("site") == site for entry in wishlist)

    users = _users_collection()
    if is_saved:
        remaining = [entry for entry in wishlist if entry.get("site") != site]
        if users is not None:
            try:
                users.document(uid).set({"wishlist": remaining}, merge=True)
            except Exception as exc:
                if "SERVICE_DISABLED" in str(exc) or "not been used in project" in str(exc):
                    _FIRESTORE_DISABLED = True
                print(f"Firestore toggle_wishlist error: {exc}")
        prof["wishlist"] = remaining
        _LOCAL_PROFILES[uid] = prof
        return False
    else:
        record = _site_record(site, location)
        if users is not None:
            try:
                users.document(uid).set(
                    {"wishlist": firestore.ArrayUnion([record])},
                    merge=True,
                )
            except Exception as exc:
                if "SERVICE_DISABLED" in str(exc) or "not been used in project" in str(exc):
                    _FIRESTORE_DISABLED = True
                print(f"Firestore toggle_wishlist error: {exc}")
        wishlist.append(record)
        prof["wishlist"] = wishlist
        _LOCAL_PROFILES[uid] = prof
        return True


def set_favorite_place(uid: str, site: str, location: str = "") -> None:
    global _FIRESTORE_DISABLED
    if not site:
        return
    record = _site_record(site, location)
    users = _users_collection()
    if users is not None:
        try:
            users.document(uid).set({"favoritePlace": record}, merge=True)
        except Exception as exc:
            if "SERVICE_DISABLED" in str(exc) or "not been used in project" in str(exc):
                _FIRESTORE_DISABLED = True
            print(f"Firestore set_favorite error: {exc}")

    prof = get_user_profile(uid)
    prof["favoritePlace"] = record
    _LOCAL_PROFILES[uid] = prof


def save_profile_picture(file_storage, filename: str):
    if file_storage is None or not file_storage.filename:
        return None
    allowed = {"png", "jpg", "jpeg", "webp"}
    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed:
        return None
    folder = Path(__file__).resolve().parents[1] / "static" / "uploads" / "profile_pics"
    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder / filename
    file_storage.save(file_path)
    return f"uploads/profile_pics/{filename}"


def increment_ar_experiences(uid: str) -> None:
    global _FIRESTORE_DISABLED
    users = _users_collection()
    if users is not None:
        try:
            users.document(uid).set(
                {"stats": {"arExperiences": firestore.Increment(1)}}, merge=True
            )
        except Exception as exc:
            if "SERVICE_DISABLED" in str(exc) or "not been used in project" in str(exc):
                _FIRESTORE_DISABLED = True
            print(f"Firestore increment_ar error: {exc}")

    prof = get_user_profile(uid)
    stats = prof.get("stats", {})
    stats["arExperiences"] = stats.get("arExperiences", 0) + 1
    prof["stats"] = stats
    _LOCAL_PROFILES[uid] = prof
