"""
Authentication views.

URLs:
    GET  /accounts/login/
    POST /accounts/
    POST /accounts/logout/
    (optional) GET /accounts/
"""
import flask
import insta4288


@insta4288.app.route("/accounts/login/", methods=["GET"])
def accounts_login_page():
    """Render the login page."""
    return flask.render_template("accounts.html")


@insta4288.app.route("/accounts/", methods=["GET"])
def accounts_get_redirect():
    """Redirect bare /accounts/ to the login page (tests expect this)."""
    return flask.redirect(flask.url_for("accounts_login_page"))


@insta4288.app.route("/accounts/logout/", methods=["POST"])
def accounts_logout():
    """Handle logout and redirect to target or login page."""
    target = flask.request.args.get("target",
                                    flask.url_for("accounts_login_page"))
    flask.session.pop("logname", None)
    return flask.redirect(target)
