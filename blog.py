import os
import re
import random
import string
import hashlib
import hmac

import jinja2
import webapp2

from google.appengine.ext import db

# Set up Jinja Environment
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

# Helper functions for verifying input
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASSWD_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASSWD_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_email(email):
    return not email or EMAIL_RE.match(email)

# Helper functions for hashing passwords
def make_salt():
    return ''.join(random.choice(string.letters) for x in range(5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
    salt = h.split(',')[1]
    return h == make_pw_hash(name, pw, salt)

# Helper functions for creating cookies
SECRET = 'Really, really, super secret string'

def make_secure_cookie(s):
    hash_str = hmac.new(SECRET, s).hexdigest()
    return '%s|%s' % (s, hash_str)

def check_secure_cookie(h):
    val = h.split('|')[0]
    if h == make_secure_cookie(val):
        return val


# Create our User registry database
class User(db.Model):
    name = db.StringProperty(required = True)
    hashed_pw = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_name(cls, name):
        return cls.all().filter('name =', name).get()


# Create our Blog database
class BlogPost(db.Model):
    author = db.ReferenceProperty(User)
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    likes = db.ListProperty(db.Key, default=None)

    def like_count(self):
        return len(self.likes)

    def get_id(self):
        return self.key().id()


# Page Handlers
# Parent page handler
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


# Signup page
class SignupHandler(Handler):
    def get(self):
        self.render('signup.html')

    def post(self):
        # Get user input
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        # Process results
        input_error = False
        user_error = ""
        passwd_error = ""
        verify_error = ""
        email_error = ""

        if not valid_username(username):
            user_error = "That's not a valid username"
            input_error = True
        if not valid_password(password):
            passwd_error = "That wasn't a valid password"
            input_error = True
        elif password != verify:
            verify_error = "Your passwords didn't match"
            input_error = True
        if not valid_email(email):
            email_error = "That's not a valid email"
            input_error = True

        # Check if this user is already in our registry
        if not input_error:
            if User.by_name(username):
                user_error = "The user already exists"
                input_error = True

        if not input_error:
            # Create user entry in database
            hashed_pw = make_pw_hash(username, password)
            u = User(name=username, hashed_pw=hashed_pw, email=email)
            u.put()
            # Set cookie to user_id
            uid = u.key().id()
            user_id = make_secure_cookie(str(uid))
            self.response.headers.add_header('Set-Cookie',
                                    'user_id=%s; Path=/' % user_id)
            # Redirect to welcome page
            self.redirect('/blog/welcome')
        else:
            self.render('signup.html', username=username, email=email,
                    user_error=user_error, passwd_error=passwd_error,
                    verify_error=verify_error, email_error=email_error)


# Login page
class LoginHandler(Handler):
    def get(self):
        self.render('login.html')

    def post(self):
        # get user input
        username = self.request.get('username')
        password = self.request.get('password')

        # check if user is in database
        u = User.by_name(username)
        if u and valid_pw(username, password, u.hashed_pw):
            # process a valid input
            # set cookie to user_id
            uid = u.key().id()
            user_id = make_secure_cookie(str(uid))
            self.response.headers.add_header('Set-Cookie',
                                    'user_id=%s; Path=/' % user_id)
            # redirect to welcome page
            self.redirect('/blog/welcome')
        else:
            # error
            error_msg = "Invalid username or password"
            self.render('login.html', error_msg=error_msg)


# Logout page
class LogoutHandler(Handler):
    def get(self):
        # Clear cookies
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        # Redirect to signup
        self.redirect('/blog/signup')


# Welcome page
class WelcomeHandler(Handler):
    def get(self):
        # Get user_id from cookie
        user_id = self.request.cookies.get('user_id')
        uid = user_id and check_secure_cookie(user_id)
        # Look up this user in the database
        user = uid and User.get_by_id(int(uid))
        if user:
            # Look up blog posts for this user
            entries = BlogPost.all().filter('author =', user).order('-created')
            self.render('welcome.html', username=user.name, entries=entries)
        else:
            self.redirect('/blog/signup')

    def post(self):
        action = self.request.get("post-action")
        if action and action == "newpost":
            self.redirect('/blog/newpost')
        elif action:
            # Parse the action
            code = action.split('|')[0]
            blog_id = int(action.split('|')[1])
            if code == "edit":
                # Edit blog
                pass
            elif code == "del":
                # Delete blog
                pass
            else:
                # Error
                self.redirect('/blog/welcome')
        else:
            # Error
            self.redirect('/blog/welcome')


# Front Blog page
class MainPage(Handler):
    def render_front(self):
        entries = db.GqlQuery("SELECT * FROM BlogPost "
                           "ORDER BY created DESC LIMIT 10")
        self.render('front.html', entries=entries)

    def get(self):
        self.render_front()


# New blog post entry page
class NewPost(Handler):
    def get(self):
        self.render('form.html')

    def post(self):
        # Get user_id from cookie
        user_id = self.request.cookies.get('user_id')
        uid = user_id and check_secure_cookie(user_id)
        # Look up this user in the database
        user = uid and User.get_by_id(int(uid))
        if user:
            subject = self.request.get('subject')
            content = self.request.get('content')

            # Error checking on input
            if subject and content:
                # Create new Blog Post
                b = BlogPost(author=user, subject=subject, content=content)
                b.put()
                # Redirect to permalink page
                blog_id = b.key().id()
                self.redirect('/blog/%d' % blog_id)
            else:
                # Error, so return to form
                error = "Please enter subject and content"
                self.render('form.html', subject=subject, content=content,
                            error=error)
        else:
            # user is invalid or not logged in
            self.redirect('/blog/login')


# Permalink blog page
class PermalinkHandler(Handler):
    def get(self, blog_id):
        entry = BlogPost.get_by_id(int(blog_id))
        self.render('permalink.html', entry=entry)


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/signup', SignupHandler),
    ('/blog/login', LoginHandler),
    ('/blog/logout', LogoutHandler),
    ('/blog/welcome', WelcomeHandler),
    ('/blog/newpost', NewPost),
    (r'/blog/(\d+)', PermalinkHandler)
], debug=True)
