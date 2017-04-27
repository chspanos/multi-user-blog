# Program to create a multi-user blog implemented with Google App Engine
# and Jinja templates.
#
# Dependencies: app.yaml
#   templates/blog-base.html
#   templates/front.html
#   templates/welcome.html
#   templates/permalink.html
#   templates/form.html
#   templates/comment.html
#   templates/login-base.html
#   templates/signup.html
#   templates/login.html
#   static/css/blog-style.css
#   static/css/login-style.css
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


# Helper functions for verifying signup and login input
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
    """ User class for our blog registry database

    Attributes:
        name - username (string, required)
        hashed_pw - hashed password (string, required)
        email - email address (string, optional)
    """
    name = db.StringProperty(required = True)
    hashed_pw = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_name(cls, name):
        """ Searches the User database for a given username and
        returns the first matching entry
        """
        return cls.all().filter('name =', name).get()


# Create our Blog database
class BlogPost(db.Model):
    """ BlogPost class for representing blog entries

    Attributes:
        author - post author (reference to User object, required)
        subject - blog subject line (string, required)
        content - blog content (text block, required)
        created - date created (date/time, automatically generated)
        likes - list of users who liked the post (list of user_ids (int))
        comments - list of comments (list of comment_ids (int))
    """
    author = db.ReferenceProperty(User)
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    likes = db.ListProperty(int, default=None)
    comments = db.ListProperty(int, default=None)

    def get_id(self):
        """ Returns blog id """
        return self.key().id()

    def valid_author(self, user):
        """ Returns True if this is a valid user and the author of
        this post.
        """
        return user and self.author.name == user.name

    def update_post_content(self, subject, content):
        """ Updates post subject and content fields.  Note: You still
        need to put() to update database.
        """
        self.subject = subject
        self.content = content

    def user_already_liked(self, user_id):
        """ Returns True if this user already liked this post """
        return int(user_id) in self.likes

    def add_like(self, user_id):
        """ Add a like from this user """
        self.likes.append(int(user_id))

    def like_count(self):
        """ Returns number of likes """
        return len(self.likes)

    def add_comment(self, cid):
        """ Adds a comment id to the comments list """
        self.comments.append(cid)

    def comment_count(self):
        """ Returns number of comments """
        return len(self.comments)

    def get_comment(self, cid):
        """ Returns comment text """
        return Comment.get_text_by_id(cid)

    def get_comment_author(self, cid):
        """ Returns comment author """
        return Comment.get_author_by_id(cid)

    def delete_comment(self, cid):
        """ Deletes this comment id from the comments list """
        self.comments.remove(cid)

    def delete_post(self):
        """ Deletes this blog post """
        # delete all comments associated with this post
        for cid in self.comments:
            Comment.delete_comment(cid)
        # delete this post
        self.delete()


# Create our comment database
class Comment(db.Model):
    """ Comment class for storing user comments.

    Attributes:
        blog_post - blog post associated with this comment (reference to
            a BlogPost object, required)
        author - comment author (reference to a User object, required)
        text - comment text (text block, required)
        created - date created (date/time, automatically generated)
    """
    blog_post = db.ReferenceProperty(BlogPost)
    author = db.ReferenceProperty(User)
    text = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    @classmethod
    def get_text_by_id(cls, cid):
        """ Looks up comment by id and returns its text """
        comment = cid and cls.get_by_id(cid)
        return comment and comment.text

    @classmethod
    def get_author_by_id(cls, cid):
        """ Looks up comment by id and returns its author's username """
        comment = cid and cls.get_by_id(cid)
        user = comment and comment.author
        return user and user.name

    def valid_author(self, user):
        """ Returns True if this is a valid user and the author of
        this comment. """
        return user and self.author.name == user.name

    def update_text(self, text):
        """ Updates comment text attribute. Note: You still
        need to put() to update database. """
        self.text = text

    @classmethod
    def delete_comment(cls, cid):
        """ Looks up comment by id and deletes it """
        comment = cid and cls.get_by_id(cid)
        if comment:
            comment.delete()


# Page Handlers
# Parent page handler
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
        return user_id and check_secure_cookie(user_id)

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


# Signup page
class SignupHandler(Handler):
    """ Signup page handler loads signup HTML template and processes
    user data to create a new User in the registry
    """
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
        if not input_error and User.by_name(username):
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
    """ Login page handler loads login HTML template and processes user
    data to retrieve an existing User from the registry.
    """
    def get(self):
        self.render('login.html')

    def post(self):
        # Get user input
        username = self.request.get('username')
        password = self.request.get('password')
        # Check if user is in database
        u = User.by_name(username)
        if u and valid_pw(username, password, u.hashed_pw):
            # Process a valid input
            # Set cookie to user_id
            uid = u.key().id()
            user_id = make_secure_cookie(str(uid))
            self.response.headers.add_header('Set-Cookie',
                                    'user_id=%s; Path=/' % user_id)
            # Redirect to welcome page
            self.redirect('/blog/welcome')
        else:
            # error
            error_msg = "Invalid username or password"
            self.render('login.html', error_msg=error_msg)


# Logout page
class LogoutHandler(Handler):
    """ Logout handler to sign a registered User out of the blog """
    def get(self):
        # Clear cookies
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        # Redirect to signup
        self.redirect('/blog/signup')


# Welcome page
class WelcomeHandler(Handler):
    """ Welcome page handler loads the welcome HTML template. This page
    displays a welcome message and control panel for this User. It
    contains a table of all the user's posts and allows them to create,
    edit, or delete their posts.
    """
    def get(self):
        # if user is logged in
        if self.user:
            # Look up blog posts for this user
            entries = BlogPost.all().filter('author =', self.user).order('-created')
            self.render('welcome.html', username=self.user.name, entries=entries)
        else:
            self.redirect('/blog/signup')


# Front Blog page
class MainPage(Handler):
    """ Main page handler for the blog loads the front HTML template.
    This page displays the most recent 10 blog posts with links to their
    corresponding permalink pages.
    """
    def get(self):
        # Get blog entries
        entries = db.GqlQuery("SELECT * FROM BlogPost "
                           "ORDER BY created DESC LIMIT 10")
        self.render('front.html', entries=entries)


# New blog post entry page
class NewPost(Handler):
    """ NewPost page handler loads the form HTML template and processes
    User input to create a new blog post and add it to the database.
    """
    def get(self):
        self.render('form.html')

    def post(self):
        if self.user:
            # Get action
            action = self.request.get('action')
            if action and action == 'Save':
                subject = self.request.get('subject')
                content = self.request.get('content')
                # Error checking on input
                if subject and content:
                    # Create new Blog Post
                    b = BlogPost(author=self.user, subject=subject,
                                content=content)
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
                # Cancel the post and redirect to welcome page
                self.redirect('/blog/welcome')
        else:
            # user is invalid or not logged in
            self.redirect('/blog/login')


# Edit blog post page
class EditPost(Handler):
    """ EditPost handler reloads the form HTML template with the contents
    of a previous blog post entry and allows the User to edit its contents.
    """
    def get(self):
        # Get post from id
        blog_id = self.get_post_id()
        post = BlogPost.get_by_id(blog_id)
        if post:
            # Check for author of post
            if self.user and post.valid_author(self.user):
                # render the form with the old content inserted
                subject = post.subject
                content = post.content
                self.render('form.html', subject=subject, content=content)
            elif self.user:
                # invalid user
                msg = "Users can only edit their own posts"
                self.render('permalink.html', entry=post, error=msg)
            else:
                # user is not logged in, so redirect to login
                self.redirect('/blog/login')
        else:
            # invalid post so redirect to welcome page
            self.redirect('/blog/welcome')

    def post(self):
        # Get post from id
        blog_id = self.get_post_id()
        blog_post = BlogPost.get_by_id(blog_id)
        if blog_post:
            # Check for author of post
            if self.user and blog_post.valid_author(self.user):
                # Get action
                action = self.request.get('action')
                if action and action == 'Save':
                    # Update content
                    subject = self.request.get('subject')
                    content = self.request.get('content')
                    # Error checking on input
                    if subject and content:
                        # Update existing Blog Post
                        blog_post.update_post_content(subject, content)
                        blog_post.put()
                        # Redirect to permalink page
                        self.redirect('/blog/%d' % blog_id)
                    else:
                        # Error, so return to form
                        error = "Please enter subject and content"
                        self.render('form.html', subject=subject,
                            content=content, error=error)
                else:
                    # Cancel the edit and redirect to permalink page
                    self.redirect('/blog/%d' % blog_id)
            elif self.user:
                # User is invalid
                msg = "Users can only edit their own posts"
                self.render('permalink.html', entry=blog_post, error=msg)
            else:
                # User is not logged in, so redirect to login
                self.redirect('/blog/login')
        else:
            # Invalid post so redirect to welcome page
            self.redirect('/blog/welcome')


# Delete post handler
class DeletePost(Handler):
    """ DeletePost page handler process a User request to delete their post
    from the blog database.
    """
    def get(self):
        # Get post from id
        blog_id = self.get_post_id()
        blog_post = BlogPost.get_by_id(blog_id)
        if blog_post:
            # Check for author of post
            if self.user and blog_post.valid_author(self.user):
                # Delete entry
                blog_post.delete_post()
                self.redirect('/blog/welcome')
            elif self.user:
                # Invalid user, action not allowed
                msg = "Users can only delete their own posts"
                self.render('permalink.html', entry=blog_post, error=msg)
            else:
                # user not logged in, so redirect to login
                self.redirect('/blog/login')
        else:
            # Invalid post, so redirect to welcome page
            self.redirect('/blog/welcome')


# Permalink blog page
class PermalinkHandler(Handler):
    """ Permalink page handler loads the permalink HTML template which
    displays a single blog post, including the blog content,
    number of likes, and all associated comments. It also allows
    registered users to like this post and create, edit, and delete
    user-owned comments.
    """
    def get(self, blog_id):
        entry = BlogPost.get_by_id(int(blog_id))
        self.render('permalink.html', entry=entry)


# Like post handler
class LikeHandler(Handler):
    """ Like handler processes a user request to "like" a blog post """
    def get(self, blog_id):
        # get blog entry
        entry = BlogPost.get_by_id(int(blog_id))
        # get user id
        uid = self.user and self.user.key().id()
        # Check if this user is allowed to like this post
        if not uid:
            # not logged in
            self.redirect('/blog/login')
        elif entry.valid_author(self.user):
            error = "Authors aren't permitted to like their own posts"
            self.render('permalink.html', entry=entry, error=error)
        elif entry.user_already_liked(uid):
            error = "Users are only permitted to like a post once"
            self.render('permalink.html', entry=entry, error=error)
        else:
            entry.add_like(uid)
            entry.put()
            self.render('permalink.html', entry=entry)


# New comment page
class NewComment(Handler):
    """ New Comment handler loads the comment HTML template and
    processes user input to create a new comment. The new comment is
    added to the Comment database and linked with the blog post.
    """
    def get(self, blog_id):
        # Get post from id
        blog_post = BlogPost.get_by_id(int(blog_id))
        self.render('comment.html', entry=blog_post)

    def post(self, blog_id):
        # Get post from id
        blog_post = BlogPost.get_by_id(int(blog_id))
        # Check user
        if self.user:
            # Get action
            action = self.request.get('action')
            if action and action == 'Save':
                # get comment text
                comment = self.request.get('comment')
                if comment:
                    # Create new Comment object
                    c = Comment(blog_post=blog_post, author=self.user,
                                text=comment)
                    c.put()
                    # Add comment to blog_post
                    cid = c.key().id()
                    blog_post.add_comment(cid)
                    blog_post.put()
                    # Redirect to permalink page
                    self.redirect('/blog/%d' % int(blog_id))
                else:
                    # Error, so return to form
                    error = "Please enter a comment"
                    self.render('comment.html', entry=blog_post, comment=comment,
                                error=error)
            else:
                # Cancel the edit and redirect to permalink page
                self.redirect('/blog/%d' % int(blog_id))
        else:
            # user is invalid or not logged in
            self.redirect('/blog/login')


# Edit comment page handler
class EditComment(Handler):
    """ EditComment handler reloads the comment HTML template with the
    current comment text and allows its User author to edit it.
    """
    def get(self, blog_id):
        # Get post from id
        blog_post = BlogPost.get_by_id(int(blog_id))
        # Get comment from id
        cid = self.get_comment_id()
        comment = Comment.get_by_id(cid)
        # Check user
        if self.user:
            if blog_post and comment and comment.valid_author(self.user):
                self.render('comment.html', entry=blog_post,
                            comment=comment.text)
            else:
                msg = "Users can only edit comments they themselves have made."
                self.render('permalink.html', entry=blog_post, error=msg)
        else:
            self.redirect('/blog/login')

    def post(self, blog_id):
        # Get post from id
        blog_post = BlogPost.get_by_id(int(blog_id))
        # Get comment from id
        cid = self.get_comment_id()
        comment = Comment.get_by_id(cid)
        # Check user
        if self.user:
            if blog_post and comment and comment.valid_author(self.user):
                # Get action
                action = self.request.get('action')
                if action and action == 'Save':
                    # get new comment
                    text = self.request.get('comment')
                    if text:
                        # Udpate comment with new content
                        comment.update_text(text)
                        comment.put()
                        # Redirect to permalink page
                        self.redirect('/blog/%d' % int(blog_id))
                    else:
                        # Error, so return to form
                        error = "Please enter a comment"
                        self.render('comment.html', entry=blog_post,
                            error=error)
                else:
                    # Cancel the edit and redirect to permalink page
                    self.redirect('/blog/%d' % int(blog_id))
            else:
                # Cancel the edit and redirect to permalink page
                self.redirect('/blog/%d' % int(blog_id))
        else:
            # user is invalid or not logged in
            self.redirect('/blog/login')


# Delete comment handler
class DeleteComment(Handler):
    """ DeleteComment handler processes a User request to remove a
    comment that they made from the blog and delete it from the
    comment database.
    """
    def get(self, blog_id):
        # Get post from id
        blog_post = BlogPost.get_by_id(int(blog_id))
        # Get comment from id
        cid = self.get_comment_id()
        comment = Comment.get_by_id(cid)
        # Check user
        if self.user:
            if blog_post and comment and comment.valid_author(self.user):
                # remove comment from blog
                blog_post.delete_comment(cid)
                blog_post.put()
                # Delete comment
                comment.delete()
                # redirect to permalink page
                self.redirect('/blog/%d' % int(blog_id))
            else:
                # Action not allowed
                error = "Users can only delete comments they have made."
                self.render('permalink.html', entry=blog_post, error=error)
        else:
            # Invalid user, action not allowed
            self.redirect('/blog/login')


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/signup', SignupHandler),
    ('/blog/login', LoginHandler),
    ('/blog/logout', LogoutHandler),
    ('/blog/welcome', WelcomeHandler),
    ('/blog/newpost', NewPost),
    ('/blog/editpost', EditPost),
    ('/blog/delpost', DeletePost),
    (r'/blog/(\d+)', PermalinkHandler),
    (r'/blog/(\d+)/like', LikeHandler),
    (r'/blog/(\d+)/comment', NewComment),
    (r'/blog/(\d+)/editcmt', EditComment),
    (r'/blog/(\d+)/delcmt', DeleteComment)
], debug=True)
