# Welcome page
import bloghandler
from models.post import BlogPost


class WelcomeHandler(bloghandler.Handler):
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
