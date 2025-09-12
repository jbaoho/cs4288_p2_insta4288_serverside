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
    # For now, hardcode the user until authentication is implemented
    logname = flask.session.get('logname')
    
    # Query the database for posts
    connection = insta4288.model.get_db()
    posts = connection.execute(
        """
        SELECT p.postid, p.filename as img_url, p.owner, 
               u.filename as owner_img_url, p.created as created,
               (SELECT COUNT(*) FROM likes WHERE postid = p.postid) as likes,
               (SELECT COUNT(*) FROM likes WHERE postid = p.postid AND owner = ?) as user_liked
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
            "SELECT owner, text FROM comments WHERE postid = ? ORDER BY commentid",
            (post_dict['postid'],)
        ).fetchall()
        post_dict['comments'] = [dict(comment) for comment in comments]
        
        posts_list.append(post_dict)
    
    context = {
        'logname': logname,
        'posts': posts_list
    }
    return flask.render_template('index.html', **context)

# @insta4288.app.route('/likes/', methods=['POST'])
# def handle_likes():
#     # Get the operation and postid from the form
#     operation = flask.request.form['operation']
#     postid = flask.request.form['postid']
#     target = flask.request.args.get('target', flask.url_for('show_index'))
    
#     # For now, just redirect back to the target
#     # You'll implement the actual like/unlike functionality later
#     return flask.redirect(target)

# @insta4288.app.route('/comments/', methods=['POST'])
# def handle_comments():
#     # Get the operation, postid, and text from the form
#     operation = flask.request.form['operation']
#     postid = flask.request.form['postid']
#     text = flask.request.form.get('text', '')
#     target = flask.request.args.get('target', flask.url_for('show_index'))
    
#     # For now, just redirect back to the target
#     # You'll implement the actual comment functionality later
#     return flask.redirect(target)


