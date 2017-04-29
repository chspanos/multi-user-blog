# Create our Blog database
from google.appengine.ext import db

from models.user import User


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

    def valid_author(self, user_obj):
        """ Returns True if this is a valid user and the author of
        this post.
        """
        return user_obj and self.author.name == user_obj.name

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

    def delete_comment(self, cid):
        """ Deletes this comment id from the comments list """
        self.comments.remove(cid)
