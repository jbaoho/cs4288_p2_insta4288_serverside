import flask
import insta4288

# Public GET endpoints that must remain accessible when logged out
_PUBLIC_GET_ENDPOINTS = {
    "accounts_login_page",   # GET /accounts/login/
    "accounts_get_redirect", # GET /accounts/ -> redirect to login
    "accounts_create",       # GET /accounts/create/
}
# Endpoints always allowed (not pages)
_PUBLIC_ENDPOINTS_GENERIC = {
    "static",
    "accounts_auth",
    "uploads",               # uploads does its own 403/404 handling
}

@insta4288.app.before_request
def require_login_for_get_pages():
    # Allow non-page endpoints outright
    if flask.request.endpoint in _PUBLIC_ENDPOINTS_GENERIC:
        return None

    # Already logged in? allow
    if flask.session.get("logname"):
        return None

    # For GET page requests, redirect to login if not in allowlist
    if flask.request.method == "GET":
        if flask.request.endpoint in _PUBLIC_GET_ENDPOINTS:
            return None
        return flask.redirect(flask.url_for("accounts_login_page"))

    # Let POSTs/others hit their own 403/400 logic
    return None
