# Program to create a multi-user blog implemented with Google App Engine
# and Jinja templates.
#
# Dependencies: app.yaml, index.yaml
#   models/user.py
#   models/post.py
#   models/user.py
#   handlers/bloghandler.py
#   handlers/mainpage.py
#   handlers/signup.py
#   handlers/login.py
#   handlers/logout.py
#   handlers/welcome.py
#   handlers/newpost.py
#   handlers/editpost.py
#   handlers/delpost.py
#   handlers/permalink.py
#   handlers/like.py
#   handlers/newcomment.py
#   handlers/editcmt.py
#   handlers/delcmt.py
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

import webapp2

# import Page Handlers
from handlers.mainpage import MainPage
from handlers.signup import SignupHandler
from handlers.login import LoginHandler
from handlers.logout import LogoutHandler
from handlers.welcome import WelcomeHandler
from handlers.newpost import NewPost
from handlers.editpost import EditPost
from handlers.delpost import DeletePost
from handlers.permalink import PermalinkHandler
from handlers.like import LikeHandler
from handlers.newcomment import NewComment
from handlers.editcmt import EditComment
from handlers.delcmt import DeleteComment

# launch the application
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
