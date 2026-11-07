"""
app.py — CONTROLLER layer (MVC architecture).

Each function below is a "route": it answers when the browser visits a URL.
A route (1) reads the request, (2) calls the model, (3) chooses a template (the VIEW).
"""

import os

from flask import Flask, abort, flash, redirect, render_template, request, url_for

import models
from validation import validate_application


def create_app(db_path=None):
    """Application factory: builds the Flask app.
    Passing a different db_path lets the tests use a temporary database."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-key-change-me"  # needed for flash messages
    app.config["DATABASE"] = db_path or os.path.join(app.root_path, "applytrack.db")

    models.init_db(app.config["DATABASE"])

    def db():
        return app.config["DATABASE"]

    # ---------- FR2: list all applications ----------
    @app.route("/")
    def index():
        applications = models.get_all_applications(db())
        return render_template(
            "index.html", applications=applications, statuses=models.STATUSES
        )

    # ---------- FR1: create a new application ----------
    @app.route("/applications/new", methods=["GET", "POST"])
    def new_application():
        if request.method == "POST":
            data, errors = validate_application(request.form)
            if errors:
                for e in errors:
                    flash(e, "error")
                return render_template(
                    "form.html", application=data, statuses=models.STATUSES, mode="new"
                ), 400
            models.create_application(db(), data)
            flash("Application added.", "success")
            return redirect(url_for("index"))
        # GET: show an empty form
        return render_template(
            "form.html", application={}, statuses=models.STATUSES, mode="new"
        )

    # ---------- FR3: edit an application ----------
    @app.route("/applications/<int:app_id>/edit", methods=["GET", "POST"])
    def edit_application(app_id):
        application = models.get_application(db(), app_id)
        if application is None:
            abort(404)
        if request.method == "POST":
            data, errors = validate_application(request.form)
            if errors:
                for e in errors:
                    flash(e, "error")
                data["id"] = app_id
                return render_template(
                    "form.html", application=data, statuses=models.STATUSES, mode="edit"
                ), 400
            models.update_application(db(), app_id, data)
            flash("Application updated.", "success")
            return redirect(url_for("index"))
        return render_template(
            "form.html", application=application, statuses=models.STATUSES, mode="edit"
        )

    # ---------- FR5: quick status change ----------
    @app.route("/applications/<int:app_id>/status", methods=["POST"])
    def change_status(app_id):
        if models.get_application(db(), app_id) is None:
            abort(404)
        status = request.form.get("status", "")
        if status not in models.STATUSES:
            flash("Invalid status.", "error")
        else:
            models.update_status(db(), app_id, status)
            flash("Status updated.", "success")
        return redirect(url_for("index"))

    # ---------- FR4: delete ----------
    @app.route("/applications/<int:app_id>/delete", methods=["POST"])
    def delete_application(app_id):
        if models.get_application(db(), app_id) is None:
            abort(404)
        models.delete_application(db(), app_id)
        flash("Application deleted.", "success")
        return redirect(url_for("index"))

    return app


# Run with:  python app.py   then open http://127.0.0.1:5000
if __name__ == "__main__":
    create_app().run(debug=True)
