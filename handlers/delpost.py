# Delete post handler
import bloghandler
import decorator
from models.post import BlogPost
from models.comment import Comment


class DeletePost(bloghandler.Handler):
    """ DeletePost page handler process a User request to delete their post
    from the blog database.
    """
    @decorator.user_logged_in
    @decorator.post_exists2
    @decorator.user_owns_post
    def get(self):
        # Get post from id
        blog_id = self.get_post_id()
        blog_post = BlogPost.get_by_id(blog_id)
        # Delete all comments associated with this post
        Comment.delete_comments(blog_post.comments)
        # Delete the post
        blog_post.delete()
        self.redirect('/blog/welcome')
