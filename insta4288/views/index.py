"""
Insta4288 index (main) view.

URLs include:
/
/likes/
/comments/
"""
import arrow
import flask
import insta4288


@insta4288.app.route('/')
def show_index():
    """Home page for standard instagram feed."""
    logname = flask.session.get('logname')

    # Query the database for posts
    connection = insta4288.model.get_db()
    posts = connection.execute(
        """
        SELECT p.postid, p.filename as img_url, p.owner,
               u.filename as owner_img_url, p.created as created,
               (SELECT COUNT(*) FROM likes WHERE postid = p.postid) as likes,
               (SELECT COUNT(*) FROM likes
               WHERE postid = p.postid AND owner = ?) as user_liked
        FROM posts p
        JOIN users u ON p.owner = u.username
        WHERE p.owner = ? OR p.owner IN (
            SELECT username2 FROM following WHERE username1 = ?
        )
        ORDER BY p.postid DESC
        """,
        (logname, logname, logname)
    ).fetchall()

    # Convert to list of dictionaries and add comments
    posts_list = []
    for post in posts:
        post_dict = dict(post)

        # Format timestamp using arrow
        post_dict['timestamp'] = arrow.get(post_dict['created']).humanize()

        # Get comments for this post
        comments = connection.execute(
            """SELECT owner, text FROM comments
            WHERE postid = ? ORDER BY commentid""",
            (post_dict['postid'],)
        ).fetchall()
        post_dict['comments'] = [dict(comment) for comment in comments]

        posts_list.append(post_dict)

    context = {
        'logname': logname,
        'posts': posts_list
    }
    return flask.render_template('index.html', **context)
