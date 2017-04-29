# Permalink blog page
import bloghandler
from models.post import BlogPost
from models.comment import Comment


class PermalinkHandler(bloghandler.Handler):
    """ Permalink page handler loads the permalink HTML template which
    displays a single blog post, including the blog content,
    number of likes, and all associated comments. It also allows
    registered users to like this post and create, edit, and delete
    user-owned comments.
    """
    def get(self, blog_id):
        entry = BlogPost.get_by_id(int(blog_id))
        comments = Comment.get_comments(entry.comments)
        self.render('permalink.html', entry=entry, comments=comments)
