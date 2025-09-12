"""
Account management pages (delete/confirm, edit profile, change password).

GET  /accounts/delete/
GET  /accounts/edit/
GET  /accounts/password/
"""

import flask
import insta4288


def _get_user_row(connection, username):
    row = connection.execute(
        """SELECT username, fullname, email, filename
        AS user_img_url FROM users WHERE username = ?""",
        (username,),
    ).fetchone()
    if row is None:
        flask.abort(404)
    return dict(row)


@insta4288.app.route("/accounts/delete/", methods=["GET"])
def accounts_delete():
    """Delete account before confirming sign-up."""
    logname = flask.session.get('logname')
    context = {"logname": logname}
    return flask.render_template("accounts_delete.html", **context)


@insta4288.app.route("/accounts/edit/", methods=["GET"])
def accounts_edit():
    """Edit account screen."""
    logname = flask.session.get('logname')
    connection = insta4288.model.get_db()
    user = _get_user_row(connection, logname)

    context = {
        "logname": logname,
        "fullname": user["fullname"],
        "email": user["email"],
        "user_img_url": user["user_img_url"],
    }
    return flask.render_template("accounts_edit.html", **context)


@insta4288.app.route("/accounts/password/", methods=["GET"])
def accounts_password():
    """Accounts password screen."""
    logname = flask.session.get('logname')
    context = {"logname": logname}
    return flask.render_template("accounts_password.html", **context)


@insta4288.app.route("/accounts/auth/", methods=["GET"])
def accounts_auth():
    """Return 200 with no content if logged in, else 403."""
    logname = flask.session.get("logname")
    if logname:
        return ("", 200)
    flask.abort(403)
