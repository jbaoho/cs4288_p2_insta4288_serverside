"""
Explore view.

URL:
    /explore/
Lists all users the logged-in user is NOT following (and is not self),
with avatar, username link, and a follow button.
"""

import flask
import insta4288


@insta4288.app.route('/explore/')
def show_explore():
    # Match your current pattern: hardcode logname until auth is implemented
    logname = flask.session.get('logname')

    connection = insta4288.model.get_db()

    # Users NOT followed by logname (and not logname), with their avatar filename
    rows = connection.execute(
        """
        SELECT u.username, u.filename AS user_img_url
        FROM users AS u
        WHERE u.username != ?
          AND u.username NOT IN (
              SELECT username2
              FROM following
              WHERE username1 = ?
          )
        ORDER BY u.username COLLATE NOCASE
        """,
        (logname, logname)
    ).fetchall()

    not_following = [dict(r) for r in rows]

    context = {
        'logname': logname,
        'not_following': not_following,
    }
    return flask.render_template('explore.html', **context)
