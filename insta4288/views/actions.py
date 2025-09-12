"""
All POST actions for Insta4288:
- /likes/
- /comments/
- /posts/
- /following/
- /accounts/  (login/create/delete/edit_account/update_password)
"""

import hashlib
import pathlib
import uuid
from typing import Optional

import flask
import insta4288

# Logger as requested
LOGGER = flask.logging.create_logger(insta4288.app)


# -----------------------------
# Helpers
# -----------------------------
def _get_logname_or_unauth_default() -> Optional[str]:
    """Return session logname if present, else None (for noauth test mode this may be None)."""
    return flask.session.get("logname")


def _require_login() -> str:
    logname = _get_logname_or_unauth_default()
    if not logname:
        flask.abort(403)
    return logname


def _uploads_dir() -> pathlib.Path:
    # Your config already uses UPLOAD_FOLDER
    return pathlib.Path(insta4288.app.config["UPLOAD_FOLDER"]).resolve()


def _save_upload_and_get_filename(file_field: str) -> str:
    """
    Save uploaded file from `file_field` and return the UUID filename.
    Aborts(400) if file missing or empty.
    """
    if file_field not in flask.request.files:
        flask.abort(400)
    fileobj = flask.request.files[file_field]
    filename = fileobj.filename or ""
    if not filename:
        flask.abort(400)

    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"

    dest = _uploads_dir() / uuid_basename
    dest.parent.mkdir(parents=True, exist_ok=True)
    fileobj.save(dest)
    return uuid_basename


def _safe_remove_upload(basename: str) -> None:
    """Remove a file in UPLOAD_FOLDER by basename (ignore if missing)."""
    if not basename:
        return
    folder = _uploads_dir()
    target = (folder / basename).resolve()
    # Prevent path traversal
    if folder in target.parents or target == folder / basename:
        try:
            target.unlink(missing_ok=True)
        except Exception:  # best-effort removal only
            LOGGER.warning("Could not remove file: %s", target)


def _hash_password(password: str) -> str:
    """Return 'sha512$salt$hash' string."""
    algorithm = "sha512"
    salt = uuid.uuid4().hex
    h = hashlib.new(algorithm)
    h.update((salt + password).encode("utf-8"))
    return "$".join([algorithm, salt, h.hexdigest()])


def _verify_password(password: str, stored: str) -> bool:
    """
    Verify plaintext password against 'algo$salt$hash'.
    Returns True when it matches.
    """
    try:
        algorithm, salt, saved_hash = stored.split("$")
    except ValueError:
        return False
    if algorithm != "sha512":
        return False
    h = hashlib.new(algorithm)
    h.update((salt + password).encode("utf-8"))
    return h.hexdigest() == saved_hash


# -----------------------------
# /likes/  (POST)
# -----------------------------
@insta4288.app.route("/likes/", methods=["POST"])
def update_likes():
    LOGGER.debug("operation = %s", flask.request.form.get("operation"))
    LOGGER.debug("postid = %s", flask.request.form.get("postid"))

    logname = _require_login()

    op = flask.request.form.get("operation", "").strip()
    postid = flask.request.form.get("postid", "").strip()
    if not postid or op not in {"like", "unlike"}:
        flask.abort(400)
    target = flask.request.args.get("target", "/")

    connection = insta4288.model.get_db()

    # Does the like exist?
    existing = connection.execute(
        "SELECT 1 FROM likes WHERE owner = ? AND postid = ?",
        (logname, postid),
    ).fetchone()

    if op == "like":
        if existing:
            flask.abort(409)
        # ensure post exists (foreign key may enforce; do a check to be explicit)
        post_row = connection.execute(
            "SELECT 1 FROM posts WHERE postid = ?",
            (postid,),
        ).fetchone()
        if not post_row:
            flask.abort(404)
        connection.execute(
            "INSERT INTO likes(owner, postid) VALUES (?, ?)",
            (logname, postid),
        )
    else:  # unlike
        if not existing:
            flask.abort(409)
        connection.execute(
            "DELETE FROM likes WHERE owner = ? AND postid = ?",
            (logname, postid),
        )

    return flask.redirect(target)


# -----------------------------
# /comments/  (POST)
# -----------------------------
@insta4288.app.route("/comments/", methods=["POST"])
def update_comments():
    logname = _require_login()

    op = flask.request.form.get("operation", "").strip()
    postid = flask.request.form.get("postid", "").strip()
    commentid = flask.request.form.get("commentid", "").strip()
    text = flask.request.form.get("text", "")
    target = flask.request.args.get("target", "/")

    connection = insta4288.model.get_db()

    if op == "create":
        # Validate
        if not postid:
            flask.abort(400)
        if text is None or text.strip() == "":
            flask.abort(400)

        # Make sure post exists (optional if FK present)
        post_row = connection.execute(
            "SELECT 1 FROM posts WHERE postid = ?",
            (postid,),
        ).fetchone()
        if not post_row:
            flask.abort(404)

        connection.execute(
            "INSERT INTO comments(owner, postid, text) VALUES (?, ?, ?)",
            (logname, postid, text),
        )
        return flask.redirect(target)

    if op == "delete":
        if not commentid:
            flask.abort(400)
        row = connection.execute(
            "SELECT owner FROM comments WHERE commentid = ?",
            (commentid,),
        ).fetchone()
        if not row:
            # Comment gone — treat like forbidden or missing. 404 is reasonable.
            flask.abort(404)
        if row["owner"] != logname:
            flask.abort(403)

        connection.execute(
            "DELETE FROM comments WHERE commentid = ?",
            (commentid,),
        )
        return flask.redirect(target)

    # Unknown op
    flask.abort(400)


# -----------------------------
# /posts/  (POST)
# -----------------------------
@insta4288.app.route("/posts/", methods=["POST"])
def update_posts():
    logname = _require_login()

    op = flask.request.form.get("operation", "").strip()
    postid = flask.request.form.get("postid", "").strip()
    # default redirect for posts: user's page
    target = flask.request.args.get("target", f"/users/{logname}/")

    connection = insta4288.model.get_db()

    if op == "create":
        # Save upload, insert post
        uuid_basename = _save_upload_and_get_filename("file")
        connection.execute(
            "INSERT INTO posts(owner, filename) VALUES (?, ?)",
            (logname, uuid_basename),
        )
        return flask.redirect(target)

    if op == "delete":
        if not postid:
            flask.abort(400)
        row = connection.execute(
            "SELECT owner, filename FROM posts WHERE postid = ?",
            (postid,),
        ).fetchone()
        if not row:
            flask.abort(404)
        if row["owner"] != logname:
            flask.abort(403)

        # Remove uploaded file
        _safe_remove_upload(row["filename"])

        # Delete DB rows. If FKs are ON DELETE CASCADE, the following single
        # delete will remove related likes/comments; otherwise do explicit deletes.
        connection.execute("DELETE FROM posts WHERE postid = ?", (postid,))
        # If needed (no CASCADE):
        # connection.execute("DELETE FROM likes WHERE postid = ?", (postid,))
        # connection.execute("DELETE FROM comments WHERE postid = ?", (postid,))

        return flask.redirect(target)

    flask.abort(400)


# -----------------------------
# /following/  (POST)
# -----------------------------
@insta4288.app.route("/following/", methods=["POST"])
def update_following():
    logname = _require_login()

    op = flask.request.form.get("operation", "").strip()
    username = flask.request.form.get("username", "").strip()
    target = flask.request.args.get("target", "/")

    if not username or op not in {"follow", "unfollow"}:
        flask.abort(400)

    connection = insta4288.model.get_db()
    # Make sure the user to follow/unfollow exists
    exists = connection.execute(
        "SELECT 1 FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    if not exists:
        flask.abort(404)

    rel = connection.execute(
        "SELECT 1 FROM following WHERE username1 = ? AND username2 = ?",
        (logname, username),
    ).fetchone()

    if op == "follow":
        if rel:
            flask.abort(409)
        connection.execute(
            "INSERT INTO following(username1, username2) VALUES (?, ?)",
            (logname, username),
        )
    else:  # unfollow
        if not rel:
            flask.abort(409)
        connection.execute(
            "DELETE FROM following WHERE username1 = ? AND username2 = ?",
            (logname, username),
        )

    return flask.redirect(target)


# -----------------------------
# /accounts/  (POST ops)
# -----------------------------
@insta4288.app.route("/accounts/", methods=["POST"])
def accounts_ops():
    """
    Handles:
      - operation=login
      - operation=create
      - operation=delete
      - operation=edit_account
      - operation=update_password
    """
    op = flask.request.form.get("operation", "").strip()
    target = flask.request.args.get("target", "/")

    connection = insta4288.model.get_db()

    # ---------- LOGIN ----------
    if op == "login":
        username = flask.request.form.get("username", "").strip()
        password = flask.request.form.get("password", "").strip()
        if not username or not password:
            flask.abort(400)

        row = connection.execute(
            "SELECT username, password FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if not row:
            flask.abort(403)
        if not _verify_password(password, row["password"]):
            flask.abort(403)

        flask.session["logname"] = row["username"]
        return flask.redirect(target)

    # ---------- CREATE ACCOUNT ----------
    if op == "create":
        username = flask.request.form.get("username", "").strip()
        password = flask.request.form.get("password", "").strip()
        fullname = flask.request.form.get("fullname", "").strip()
        email = flask.request.form.get("email", "").strip()

        # Validate required fields
        if not (username and password and fullname and email):
            flask.abort(400)

        # Username availability
        exists = connection.execute(
            "SELECT 1 FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if exists:
            flask.abort(409)

        # Save user photo (required)
        photo_basename = _save_upload_and_get_filename("file")

        # Hash password and insert
        pwd_db = _hash_password(password)
        connection.execute(
            """
            INSERT INTO users(username, password, fullname, email, filename)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, pwd_db, fullname, email, photo_basename),
        )

        # Log in new user
        flask.session["logname"] = username
        return flask.redirect(target)

    # Require login for the rest
    logname = _require_login()

    # ---------- DELETE ACCOUNT ----------
    if op == "delete":
        # Collect files to remove: user icon + all post images
        posts = connection.execute(
            "SELECT filename FROM posts WHERE owner = ?",
            (logname,),
        ).fetchall()
        user_row = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (logname,),
        ).fetchone()

        # Delete user row (and rely on ON DELETE CASCADE for related tables)
        connection.execute("DELETE FROM users WHERE username = ?", (logname,))

        # Remove files after DB delete
        for p in posts:
            _safe_remove_upload(p["filename"])
        if user_row:
            _safe_remove_upload(user_row["filename"])

        # Clear session
        flask.session.pop("logname", None)
        return flask.redirect(target)

    # ---------- EDIT ACCOUNT ----------
    if op == "edit_account":
        fullname = flask.request.form.get("fullname", "").strip()
        email = flask.request.form.get("email", "").strip()
        if not fullname or not email:
            flask.abort(400)

        # Old filename (if we need to replace)
        current = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (logname,),
        ).fetchone()
        if not current:
            flask.abort(404)
        old_basename = current["filename"]

        # If file provided and not empty, replace photo
        file_field_present = "file" in flask.request.files and flask.request.files["file"].filename
        if file_field_present:
            new_basename = _save_upload_and_get_filename("file")
            connection.execute(
                "UPDATE users SET fullname = ?, email = ?, filename = ? WHERE username = ?",
                (fullname, email, new_basename, logname),
            )
            # Delete old image after successful update
            _safe_remove_upload(old_basename)
        else:
            connection.execute(
                "UPDATE users SET fullname = ?, email = ? WHERE username = ?",
                (fullname, email, logname),
            )

        return flask.redirect(target)

    # ---------- UPDATE PASSWORD ----------
    if op == "update_password":
        old = flask.request.form.get("password", "").strip()
        new1 = flask.request.form.get("new_password1", "").strip()
        new2 = flask.request.form.get("new_password2", "").strip()
        if not (old and new1 and new2):
            flask.abort(400)

        row = connection.execute(
            "SELECT password FROM users WHERE username = ?",
            (logname,),
        ).fetchone()
        if not row or not _verify_password(old, row["password"]):
            flask.abort(403)

        if new1 != new2:
            flask.abort(401)

        new_db = _hash_password(new1)
        connection.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (new_db, logname),
        )
        return flask.redirect(target)

    # Unknown operation
    flask.abort(400)
