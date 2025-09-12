# views/uploads.py (or wherever you keep it)
import pathlib
import flask
import insta4288

@insta4288.app.route("/uploads/<path:filename>")
def uploads(filename):
    """
    Serve uploaded files to authenticated users only.

    - If NOT logged in: abort(403)
    - If logged in but file missing or invalid path: abort(404)
    """
    # 1) Require login
    if not flask.session.get("logname"):
        flask.abort(403)

    # 2) Resolve path safely and ensure it's inside UPLOAD_FOLDER
    upload_dir = pathlib.Path(insta4288.app.config["UPLOAD_FOLDER"]).resolve()
    target_path = (upload_dir / filename).resolve()

    # Prevent path traversal
    if upload_dir not in target_path.parents and target_path != upload_dir / filename:
        flask.abort(404)

    # 3) Ensure file exists
    if not target_path.exists() or not target_path.is_file():
        flask.abort(404)

    # 4) Serve the file (send_from_directory safely joins dir+filename)
    return flask.send_from_directory(upload_dir, filename)
