# Delete post handler
import bloghandler
from models.post import BlogPost
from models.comment import Comment


class DeletePost(bloghandler.Handler):
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
                # Delete all comments associated with this post
                Comment.delete_comments(blog_post.comments)
                # Delete the post
                blog_post.delete()
                self.redirect('/blog/welcome')
            elif self.user:
                # Invalid user, action not allowed
                msg = "Users can only delete their own posts"
                comments = Comment.get_comments(blog_post.comments)
                self.render('permalink.html', entry=blog_post,
                        comments=comments, error=msg)
            else:
                # user not logged in, so redirect to login
                self.redirect('/blog/login')
        else:
            # Invalid post, so redirect to welcome page
            self.redirect('/blog/welcome')
