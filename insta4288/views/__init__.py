"""Views, one for each Insta4288 page."""
from insta4288.views.index import show_index
from insta4288.views.uploads import uploads
from insta4288.views.users import show_user
from insta4288.views.posts import show_post
from insta4288.views.explore import show_explore
from insta4288.views.accounts import accounts_login_page, accounts_get_redirect, accounts_logout
from insta4288.views.accounts_create import accounts_create
from insta4288.views.accounts_manage import accounts_delete, accounts_edit, accounts_password, accounts_auth
from insta4288.views.actions import update_likes, update_comments, update_posts, update_following, accounts_ops
from insta4288.views.auth_gate import require_login_for_get_pages