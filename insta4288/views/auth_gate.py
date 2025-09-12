"""Authentication/login setup."""

import flask
import insta4288

# Public GET endpoints that must remain accessible when logged out
_PUBLIC_GET_ENDPOINTS = {
    "accounts_login_page",
    "accounts_get_redirect",
    "accounts_create",
}
# Endpoints always allowed (not pages)
_PUBLIC_ENDPOINTS_GENERIC = {
    "static",
    "accounts_auth",
    "uploads",
}


@insta4288.app.before_request
def require_login_for_get_pages():
    """Require login forall GET pages except for public endpoints."""
    if flask.request.endpoint in _PUBLIC_ENDPOINTS_GENERIC:
        return None

    # Already logged in
    if flask.session.get("logname"):
        return None

    # Redirect to login if page not in allowed list
    if flask.request.method == "GET":
        if flask.request.endpoint in _PUBLIC_GET_ENDPOINTS:
            return None
        return flask.redirect(flask.url_for("accounts_login_page"))

    return None
