"""
Create account page.

URLs:
    GET /accounts/create/   -> signup page
"""

import flask
import insta4288


@insta4288.app.route("/accounts/create/", methods=["GET"])
def accounts_create():
    """Render create account page unless logged in (then redirect to /accounts/edit/)."""
    if flask.session.get("logname"):
        return flask.redirect(flask.url_for("accounts_edit"))

    return flask.render_template("accounts_create.html")

