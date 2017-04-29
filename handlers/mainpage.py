# Front Blog page
from google.appengine.ext import db

import bloghandler


class MainPage(bloghandler.Handler):
    """ Main page handler for the blog loads the front HTML template.
    This page displays the most recent 10 blog posts with links to their
    corresponding permalink pages.
    """
    def get(self):
        # Get blog entries
        entries = db.GqlQuery("SELECT * FROM BlogPost "
                           "ORDER BY created DESC LIMIT 10")
        self.render('front.html', entries=entries)
