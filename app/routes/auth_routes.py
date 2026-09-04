from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.services import firebase_service

auth_bp = Blueprint("auth", __name__)


def _start_session(name: str, email: str, uid: str = "") -> None:
	session["user"] = {"email": email, "name": name, "uid": uid}


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		email = request.form.get("email", "").strip().lower()
		password = request.form.get("password", "")
		if not email or not password:
			flash("Enter your email and password to continue.", "error")
			return render_template("auth/login.html"), 400

		user, error = firebase_service.verify_user(email, password)
		if error or user is None:
			flash(error or "Incorrect email or password.", "error")
			return render_template("auth/login.html"), 401

		_start_session(user.display_name, user.email, user.uid)
		flash("Welcome back to HeritageAR.", "success")
		return redirect(url_for("home.index"))
	return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "POST":
		name = request.form.get("name", "").strip()
		email = request.form.get("email", "").strip().lower()
		password = request.form.get("password", "")
		if not name or not email or len(password) < 6:
			flash("Add your name, a valid email, and a password of at least 6 characters.", "error")
			return render_template("auth/register.html"), 400

		user, error = firebase_service.create_user(name, email, password)
		if error or user is None:
			flash(error or "Could not create the account.", "error")
			return render_template("auth/register.html"), 400

		_start_session(name, email, user.uid)
		flash("Your HeritageAR account is ready.", "success")
		return redirect(url_for("home.index"))
	return render_template("auth/register.html")


@auth_bp.get("/logout")
def logout():
	session.pop("user", None)
	flash("You have been signed out.", "success")
	return redirect(url_for("home.index"))
