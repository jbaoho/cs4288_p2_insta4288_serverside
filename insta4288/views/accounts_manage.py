"""
Account management pages (delete/confirm, edit profile, change password).

GET  /accounts/delete/    -> confirmation page
GET  /accounts/edit/      -> edit profile
GET  /accounts/password/  -> change password form
"""

import flask
import insta4288


def _get_user_row(connection, username):
    row = connection.execute(
        "SELECT username, fullname, email, filename AS user_img_url FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    if row is None:
        # In your seed DB, this exists; if not, fail fast.
        flask.abort(404)
    return dict(row)


@insta4288.app.route("/accounts/delete/", methods=["GET"])
def accounts_delete():
    logname = flask.session.get('logname')
    # No DB needed for the confirm screen besides printing the username
    context = {"logname": logname}
    return flask.render_template("accounts_delete.html", **context)


@insta4288.app.route("/accounts/edit/", methods=["GET"])
def accounts_edit():
    logname = flask.session.get('logname')
    connection = insta4288.model.get_db()
    user = _get_user_row(connection, logname)

    context = {
        "logname": logname,
        "fullname": user["fullname"],
        "email": user["email"],
        "user_img_url": user["user_img_url"],  # filename only
    }
    return flask.render_template("accounts_edit.html", **context)


@insta4288.app.route("/accounts/password/", methods=["GET"])
def accounts_password():
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
