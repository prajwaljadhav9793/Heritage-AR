from flask import Blueprint, flash, redirect, render_template, request, session, url_for

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		email = request.form.get("email", "").strip().lower()
		if not email or not request.form.get("password"):
			flash("Enter your email and password to continue.", "error")
		else:
			session["user"] = {"email": email, "name": email.split("@")[0].replace(".", " ").title()}
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
		else:
			session["user"] = {"email": email, "name": name}
			flash("Your HeritageAR account is ready.", "success")
			return redirect(url_for("home.index"))
	return render_template("auth/register.html")


@auth_bp.get("/logout")
def logout():
	session.pop("user", None)
	flash("You have been signed out.", "success")
	return redirect(url_for("home.index"))
