"""
Single post view.

URL:
    /posts/<postid_url_slug>/
"""

import arrow
import flask
import insta4288


@insta4288.app.route('/posts/<postid_url_slug>/')
def show_post(postid_url_slug):
    """Show a single post page (same info as /, but for one post)."""
    # Hardcode logged-in user to match your current pattern
    logname = flask.session.get('logname')

    connection = insta4288.model.get_db()

    # Fetch the post (or 404 if not found)
    row = connection.execute(
        """
        SELECT
            p.postid,
            p.filename AS img_url,
            p.owner,
            u.filename AS owner_img_url,
            p.created AS created,
            (
              SELECT COUNT(*) FROM likes WHERE postid = p.postid
            ) AS likes,
            (
              SELECT COUNT(*) FROM likes WHERE postid = p.postid AND owner = ?
            ) AS user_liked
        FROM posts AS p
        JOIN users AS u ON u.username = p.owner
        WHERE p.postid = ?
        """,
        (logname, postid_url_slug)
    ).fetchone()

    if row is None:
        flask.abort(404)

    post = dict(row)
    post['timestamp'] = arrow.get(post['created']).humanize()

    # Load comments (include commentid for delete buttons)
    comments_rows = connection.execute(
        """
        SELECT commentid, owner, text
        FROM comments
        WHERE postid = ?
        ORDER BY commentid
        """,
        (post['postid'],)
    ).fetchall()

    comments = []
    for c in comments_rows:
        cd = dict(c)
        # Optional: mark a caption if you distinguish it; otherwise default False
        cd['is_caption'] = False
        comments.append(cd)

    context = {
        'logname': logname,
        'postid': post['postid'],
        'owner': post['owner'],
        'owner_img_url': post['owner_img_url'],  # filename only
        'img_url': post['img_url'],              # filename only
        'likes': post['likes'],
        'user_liked': post['user_liked'],        # available if you later add like/unlike UI
        'timestamp': post['timestamp'],
        'comments': comments,
    }
    return flask.render_template('post.html', **context)
