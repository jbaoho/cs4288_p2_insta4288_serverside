"""
Explore view.

URL:
    /explore/
"""

import flask
import insta4288


@insta4288.app.route('/explore/')
def show_explore():
    """Render the explore page."""
    logname = flask.session.get('logname')

    connection = insta4288.model.get_db()

    # Query users not followed by logname
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
