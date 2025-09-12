"""
Insta4288 user view.

URLs include:
/users/<user_url_slug>/
/users/<user_url_slug>/followers/
/users/<user_url_slug>/following/
/posts/<postid_url_slug>/
"""

import flask
import insta4288


def _get_user_or_404(connection, username):
    """Fetch a user row or abort 404 if not found."""
    row = connection.execute(
        """
        SELECT username, fullname, filename AS user_img_url
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()
    if row is None:
        flask.abort(404)
    return dict(row)


@insta4288.app.route('/users/<user_url_slug>/')
def show_user(user_url_slug):
    """User profile page."""
    # For now, hardcode logged-in user (to match your index.py pattern)
    logname = flask.session.get('logname')

    connection = insta4288.model.get_db()

    # Ensure the requested user exists; 404 if not
    user_row = _get_user_or_404(connection, user_url_slug)

    # Aggregate counts
    total_posts = connection.execute(
        "SELECT COUNT(*) AS cnt FROM posts WHERE owner = ?",
        (user_url_slug,)
    ).fetchone()['cnt']

    followers_cnt = connection.execute(
        "SELECT COUNT(*) AS cnt FROM following WHERE username2 = ?",
        (user_url_slug,)
    ).fetchone()['cnt']

    following_cnt = connection.execute(
        "SELECT COUNT(*) AS cnt FROM following WHERE username1 = ?",
        (user_url_slug,)
    ).fetchone()['cnt']

    # Relationship: does logname follow this profile user?
    rel_row = connection.execute(
        """
        SELECT 1
        FROM following
        WHERE username1 = ? AND username2 = ?
        """,
        (logname, user_url_slug)
    ).fetchone()
    logname_follows_username = rel_row is not None

    # Posts (small thumbnails)
    posts = connection.execute(
        """
        SELECT postid, filename AS img_url
        FROM posts
        WHERE owner = ?
        ORDER BY postid DESC
        """,
        (user_row['username'],)
    ).fetchall()
    posts_list = [dict(p) for p in posts]

    context = {
        'logname': logname,
        'username': user_row['username'],
        'fullname': user_row['fullname'],
        'total_posts': total_posts,
        'followers': followers_cnt,
        'following': following_cnt,
        'logname_follows_username': logname_follows_username,
        'posts': posts_list,
    }
    return flask.render_template('user.html', **context)


@insta4288.app.route('/users/<user_url_slug>/followers/')
def show_followers(user_url_slug):
    """Followers list page: users who follow user_url_slug."""
    logname = flask.session.get('logname')
    connection = insta4288.model.get_db()

    # 404 if the profile user doesn't exist
    _ = _get_user_or_404(connection, user_url_slug)

    # List followers: username1 follows username2
    # Here we want rows where username2 == user_url_slug (i.e., followers of user_url_slug)
    rows = connection.execute(
        """
        SELECT u.username, u.filename AS user_img_url
        FROM following f
        JOIN users u ON u.username = f.username1
        WHERE f.username2 = ?
        ORDER BY u.username COLLATE NOCASE
        """,
        (user_url_slug,)
    ).fetchall()

    followers = []
    for r in rows:
        follower = dict(r)

        # Relationship from logname -> this follower user
        rel = connection.execute(
            """
            SELECT 1
            FROM following
            WHERE username1 = ? AND username2 = ?
            """,
            (logname, follower['username'])
        ).fetchone()
        follower['logname_follows_username'] = rel is not None

        followers.append(follower)

    context = {
        'logname': logname,
        'username': user_url_slug,  # profile’s username for the header
        'followers': followers,
    }
    return flask.render_template('followers.html', **context)


@insta4288.app.route('/users/<user_url_slug>/following/')
def show_following(user_url_slug):
    """Following list page: users that user_url_slug is following."""
    logname = flask.session.get('logname')
    connection = insta4288.model.get_db()

    # 404 if the profile user doesn't exist
    _ = _get_user_or_404(connection, user_url_slug)

    # List accounts that user_url_slug is following:
    # username1 follows username2, so we want username1 == user_url_slug
    rows = connection.execute(
        """
        SELECT u.username, u.filename AS user_img_url
        FROM following f
        JOIN users u ON u.username = f.username2
        WHERE f.username1 = ?
        ORDER BY u.username COLLATE NOCASE
        """,
        (user_url_slug,)
    ).fetchall()

    following = []
    for r in rows:
        person = dict(r)

        # Relationship from logname -> this user
        rel = connection.execute(
            """
            SELECT 1
            FROM following
            WHERE username1 = ? AND username2 = ?
            """,
            (logname, person['username'])
        ).fetchone()
        person['logname_follows_username'] = rel is not None

        following.append(person)

    context = {
        'logname': logname,
        'username': user_url_slug,  # profile’s username for the header
        'following': following,
    }
    return flask.render_template('following.html', **context)
