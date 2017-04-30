# Parent blog page handler
import os

import jinja2
import webapp2
from google.appengine.ext import db

import utils
import decorator
from models.user import User
from models.post import BlogPost
from models.comment import Comment

# Set up Jinja Environment

one_level_up_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
template_dir = os.path.normpath(one_level_up_dir)
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)


class Handler(webapp2.RequestHandler):
    """ Parent page handler class """
    def write(self, *a, **kw):
        """ Boilerplate write method """
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        """ Boilerplate render_str method """
        # add user to the parameter list automatically
        params['user'] = self.user
        # set template and call render like before
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        """ Boilerplace render method """
        self.write(self.render_str(template, **kw))

    def get_uid_from_cookie(self):
        """ Get user_id from cookie and check if valid. Returns valid id. """
        user_id = self.request.cookies.get('user_id')
        return user_id and utils.check_secure_cookie(user_id)

    def initialize(self, *a, **kw):
        """ Overwrites standard initialize method to also check for and
        load user info from cookie
        """
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.get_uid_from_cookie()
        self.user = uid and User.get_by_id(int(uid))

    def get_post_id(self):
        """ Queries page input for blog_id and returns it as an integer. """
        return int(self.request.get('blog_id'))

    def get_comment_id(self):
        """ Queries page input for comment id and returns it as an int. """
        return int(self.request.get('cid'))

    def get_valid_comment(self, cid):
        """ Looks up comment by its id and returns comment """
        key = db.Key.from_path('Comment',int(cid))
        cmt = db.get(key)
        return cmt
