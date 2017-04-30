# Define decorator functions for checking pages
from google.appengine.ext import db


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

def comment_exists(function):
    """ Decorator function to check for valid comment_id and
    print error message is not valid
    """
    def comment_wrapper(self, cid):
        key = db.Key.from_path('Comment', int(cid))
        cmt = db.get(key)
        if cmt:
            return function(self, cid)
        else:
            self.error(404)
            return
    return comment_wrapper

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
