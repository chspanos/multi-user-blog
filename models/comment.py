# Create our comment database
from google.appengine.ext import db

from models.post import BlogPost
from models.user import User

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
    def get_comments(cls, cid_list):
        """ Given a list of comment_ids, looks them up and returns the
        list of corresponding comment objects
        """
        comment_list = []
        for cid in cid_list:
            cmt = cls.get_by_id(cid)
            if cmt:
                comment_list.append(cmt)
        return comment_list

    def get_author(self):
        """ Returns author's username for this comment """
        user_obj = self.author
        return user_obj and user_obj.name

    def get_id(self):
        """ Returns comment id """
        return self.key().id()

    @classmethod
    def get_author_by_id(cls, cid):
        """ Looks up comment by id and returns its author's username """
        comment = cid and cls.get_by_id(int(cid))
        user_obj = comment and comment.author
        return user_obj and user_obj.name

    def valid_author(self, user_obj):
        """ Returns True if this is a valid user and the author of
        this comment. """
        return user_obj and self.author.name == user_obj.name

    def update_text(self, text):
        """ Updates comment text attribute. Note: You still
        need to put() to update database. """
        self.text = text

    @classmethod
    def delete_comment(cls, cid):
        """ Looks up comment by id and deletes it """
        cmt = cid and cls.get_by_id(int(cid))
        if cmt:
            cmt.delete()

    @classmethod
    def delete_comments(cls, cid_list):
        """ Deletes the comments on the given list of ids """
        for cid in cid_list:
            cls.delete_comment(cid)
