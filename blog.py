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
    likes = db.ListProperty(int, default=None)
    comments = db.ListProperty(int, default=None)

    def get_id(self):
        return self.key().id()

    def valid_author(self, user_id):
        ''' Returns True if this is a valid user and the author of
        this post. '''
        user = user_id and User.get_by_id(int(user_id))
        return user and self.author.name == user.name

    def update_post_content(self, subject, content):
        ''' Updates post subject and content fields. Note: You still
        need to put() to update database. '''
        self.subject = subject
        self.content = content

    def user_already_liked(self, user_id):
        '''Returns True if this user already liked this post.'''
        return int(user_id) in self.likes

    def add_like(self, user_id):
        ''' Add a like from this user '''
        self.likes.append(int(user_id))

    def like_count(self):
        ''' Returns number of likes. '''
        return len(self.likes)

    def add_comment(self, cid):
        ''' Adds a comment id to the comments list '''
        self.comments.append(cid)

    def comment_count(self):
        ''' Returns number of comments '''
        return len(self.comments)

    def get_comment(self, cid):
        ''' Returns comment text '''
        return Comment.get_text_by_id(cid)

    def get_comment_author(self, cid):
        ''' Returns comment author '''
        return Comment.get_author_by_id(cid)


# Create our comment database
class Comment(db.Model):
    blog_post = db.ReferenceProperty(BlogPost)
    author = db.ReferenceProperty(User)
    text = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    @classmethod
    def get_text_by_id(cls, cid):
        ''' Looks up comment by id and returns text '''
        comment = cid and cls.get_by_id(cid)
        return comment and comment.text

    @classmethod
    def get_author_by_id(cls, cid):
        ''' Looks up comment by id and returns author name'''
        comment = cid and cls.get_by_id(cid)
        user = comment and comment.author
        return user and user.name

    def valid_author(self, user_id):
        ''' Returns True if this is a valid user and the author of
        this comment. '''
        user = user_id and User.get_by_id(int(user_id))
        return user and self.author.name == user.name

    def update_text(self, text):
        ''' Updates comment text field. Note: You still
        need to put() to update database. '''
        self.text = text


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

    def get_post_id(self):
        ''' Queries page input for blog_id and returns it as an integer. '''
        return int(self.request.get('blog_id'))

    def get_uid_from_cookie(self):
        ''' Get user_id from cookie and check if valid. Returns valid id. '''
        user_id = self.request.cookies.get('user_id')
        return user_id and check_secure_cookie(user_id)

    def get_comment_id(self):
        ''' Queries page input for comment id and returns it as an int. '''
        return int(self.request.get('cid'))


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
            post_id = int(action.split('|')[1])
            if code == "edit":
                # Edit blog post
                self.redirect('/blog/editpost?blog_id=%d' % post_id)
            elif code == "del":
                # Delete blog post
                self.redirect('/blog/delpost?blog_id=%d' % post_id)
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
        uid = self.get_uid_from_cookie()
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


# Edit blog post page
class EditPost(Handler):
    def get(self):
        # Get post from id
        blog_id = self.get_post_id()
        post = BlogPost.get_by_id(blog_id)
        if post:
            # Get user_id from cookie
            uid = self.get_uid_from_cookie()
            # Check for author of post
            if uid and post.valid_author(uid):
                # render the form with the old content inserted
                subject = post.subject
                content = post.content
                self.render('form2.html', subject=subject, content=content)
            else:
                # invalid user so redirect to login
                self.redirect('/blog/login')
        else:
            # invalid post so redirect to welcome page
            self.redirect('/blog/welcome')

    def post(self):
        # Get post from id
        blog_id = self.get_post_id()
        blog_post = BlogPost.get_by_id(blog_id)
        if blog_post:
            # Get user_id from cookie
            uid = self.get_uid_from_cookie()
            # Check for author of post
            if uid and blog_post.valid_author(uid):
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
                        self.render('form2.html', subject=subject, content=content,
                                    error=error)
                else:
                    # Cancel the edit and redirect to permalink page
                    self.redirect('/blog/%d' % blog_id)
            else:
                # User is invalid or not logged in
                self.redirect('/blog/login')
        else:
            # Invalid post so redirect to welcome page
            self.redirect('/blog/welcome')


# Delete post handler
class DeletePost(Handler):
    def get(self):
        # Get post from id
        blog_id = self.get_post_id()
        blog_post = BlogPost.get_by_id(blog_id)
        if blog_post:
            # Get user_id from cookie
            uid = self.get_uid_from_cookie()
            # Check for author of post
            if uid and blog_post.valid_author(uid):
                # Delete entry
                blog_post.delete()
                self.redirect('/blog/welcome')
            else:
                # Invalid user, action not allowed
                self.redirect('/blog/login')
        else:
            # Invalid post, so redirect to welcome page
            self.redirect('/blog/welcome')


# Permalink blog page
class PermalinkHandler(Handler):
    def get(self, blog_id):
        entry = BlogPost.get_by_id(int(blog_id))
        self.render('permalink.html', entry=entry)

    def post(self, blog_id):
        entry = BlogPost.get_by_id(int(blog_id))
        # Get user_id from cookie
        uid = self.get_uid_from_cookie()
        # Get action
        action = self.request.get('action')
        error = ""
        if action == 'Like':
            # Check if this user is allowed to like this post
            if not uid:
                # not logged in
                self.redirect('/blog/login')
            elif entry.valid_author(uid):
                error = "Authors aren't permitted to like their own posts"
                self.render('permalink.html', entry=entry, error=error)
            elif entry.user_already_liked(uid):
                error = "Users are only permitted to like a post once"
                self.render('permalink.html', entry=entry, error=error)
            else:
                entry.add_like(uid)
                entry.put()
                self.render('permalink.html', entry=entry)
        elif action == 'Comment':
            self.redirect('/blog/comment?blog_id=%d' % int(blog_id))
        else:
            error = "Invalid action"
            self.render('permalink.html', entry=entry, error=error)


class NewComment(Handler):
    def get(self):
        # Get post from id
        blog_id = self.get_post_id()
        blog_post = BlogPost.get_by_id(blog_id)
        self.render('comment.html', entry=blog_post)

    def post(self):
        # Get post from id
        blog_id = self.get_post_id()
        blog_post = BlogPost.get_by_id(blog_id)
        # Get user_id from cookie and lookup in User database
        uid = self.get_uid_from_cookie()
        user = uid and User.get_by_id(int(uid))
        if user:
            # Get action
            action = self.request.get('action')
            if action and action == 'Save':
                # get comment text
                comment = self.request.get('comment')
                if comment:
                    # Create new Comment object
                    c = Comment(blog_post=blog_post, author=user, text=comment)
                    c.put()
                    # Add comment to blog_post
                    cid = c.key().id()
                    blog_post.add_comment(cid)
                    blog_post.put()
                    # Redirect to permalink page
                    self.redirect('/blog/%d' % blog_id)
                else:
                    # Error, so return to form
                    error = "Please enter a comment"
                    self.render('comment.html', entry=blog_post, comment=comment,
                                error=error)
            else:
                # Cancel the edit and redirect to permalink page
                self.redirect('/blog/%d' % blog_id)
        else:
            # user is invalid or not logged in
            self.redirect('/blog/login')


class EditComment(Handler):
    def get(self):
        # Get post from id
        blog_id = self.get_post_id()
        blog_post = BlogPost.get_by_id(blog_id)
        # Get comment from id
        cid = self.get_comment_id()
        comment = Comment.get_by_id(cid)
        # Get user_id from cookie
        uid = self.get_uid_from_cookie()
        if uid:
            if blog_post and comment and comment.valid_author(uid):
                self.render('comment.html', entry=blog_post, comment=comment.text)
            else:
                msg = "Users can only edit comments they themselves have made. " \
                    "Press either button to return to Permalink page."
                self.render('comment.html', entry=blog_post,
                    comment=comment.text, error=msg)
        else:
            self.redirect('/blog/login')

    def post(self):
        # Get post from id
        blog_id = self.get_post_id()
        blog_post = BlogPost.get_by_id(blog_id)
        # Get comment from id
        cid = self.get_comment_id()
        comment = Comment.get_by_id(cid)
        # Get user_id from cookie
        uid = self.get_uid_from_cookie()
        if uid:
            if blog_post and comment and comment.valid_author(uid):
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
                        self.redirect('/blog/%d' % blog_id)
                    else:
                        # Error, so return to form
                        error = "Please enter a comment"
                        self.render('comment.html', entry=blog_post,
                            error=error)
                else:
                    # Cancel the edit and redirect to permalink page
                    self.redirect('/blog/%d' % blog_id)
            else:
                # Cancel the edit and redirect to permalink page
                self.redirect('/blog/%d' % blog_id)
        else:
            # user is invalid or not logged in
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
    ('/blog/comment', NewComment),
    ('/blog/editcmt', EditComment)
], debug=True)
