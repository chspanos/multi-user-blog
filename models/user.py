# Create our User registry database
from google.appengine.ext import db

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
