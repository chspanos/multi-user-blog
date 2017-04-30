# Define decorator functions for checking pages
from google.appengine.ext import db

from models.comment import Comment

def user_logged_in(function):
    """ Decorator function to check that the user is logged in.
    If not, redirects to login page.
    """
    def login_wrapper(self, *args):
        if self.user:
            function(self, *args)
        else:
            self.redirect('/blog/login')
    return login_wrapper

def post_exists(function):
    """ Decorator function to check for valid post_id and
    print error message if not valid
    """
    def post_wrapper(self, blog_id):
        key = db.Key.from_path('BlogPost', int(blog_id))
        blog_post = db.get(key)
        if blog_post:
            return function(self, blog_id)
        else:
            self.error(404)
            return
    return post_wrapper

def post_exists2(function):
    """ Decorator function to check for valid post_id. This version
    extracts the blog_id from the page request. On failure, it redirects
    to the user's welcome page.
    """
    def post2_wrapper(self, *args):
        blog_id = self.request.get('blog_id')
        key = db.Key.from_path('BlogPost', int(blog_id))
        blog_post = db.get(key)
        if blog_post:
            return function(self, *args)
        else:
            self.redirect('/blog/welcome')
    return post2_wrapper

def comment_exists(function):
    """ Decorator function to check for valid comment_id and
    print error message if not valid. This function extracts
    the comment id from the page request.
    """
    def comment_wrapper(self, *args):
        # Get comment id from request
        cid = self.request.get('cid')
        key = db.Key.from_path('Comment', int(cid))
        cmt = db.get(key)
        if cmt:
            return function(self, *args)
        else:
            self.error(404)
            return
    return comment_wrapper

def user_owns_post(function):
    """ Decorator function to check if user is the author
    of this post. If not, it redirects to the permalink page for
    the post and prints an error message.
    """
    def post_owner_wrapper(self):
        # Get blog id
        blog_id = self.request.get('blog_id')
        key = db.Key.from_path('BlogPost', int(blog_id))
        blog_post = db.get(key)
        # Check for author of post
        if blog_post.valid_author(self.user):
            return function(self)
        else:
            # Invalid user
            msg = "Users can only edit or delete their own posts"
            comments = Comment.get_comments(blog_post.comments)
            self.render('permalink.html', entry=blog_post,
                    comments=comments, error=msg)
    return post_owner_wrapper

def user_owns_comment(function):
    """ Decorator function to check if user is the author of
    this comment. If not, it redirects to the permalink page for the
    post and prints an error message.
    """
    def cmt_owner_wrapper(self, blog_id):
        # Get post from id
        key = db.Key.from_path('BlogPost', int(blog_id))
        blog_post = db.get(key)
        # Get comment from page request
        cid = self.request.get('cid')
        key = db.Key.from_path('Comment', int(cid))
        cmt = db.get(key)
        # Check user
        if cmt.valid_author(self.user):
            return function(self, blog_id)
        else:
            # Invalid user
            msg = "Users can only edit or delete comments they have made."
            comments = Comment.get_comments(blog_post.comments)
            self.render('permalink.html', entry=blog_post,
                    comments=comments, error=msg)
    return cmt_owner_wrapper
