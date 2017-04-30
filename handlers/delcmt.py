# Delete comment handler
import bloghandler
import decorator
from models.post import BlogPost
from models.comment import Comment


class DeleteComment(bloghandler.Handler):
    """ DeleteComment handler processes a User request to remove a
    comment that they made from the blog and delete it from the
    comment database.
    """
    @decorator.user_logged_in
    @decorator.post_exists
    def get(self, blog_id):
        # Get post from id
        blog_post = BlogPost.get_by_id(int(blog_id))
        # Get comment from id
        cid = self.request.get('cid')
        cmt = self.get_valid_comment(cid)
        # Check user
        if blog_post and cmt and cmt.valid_author(self.user):
            # remove comment from blog
            blog_post.delete_comment(int(cid))
            blog_post.put()
            # Delete comment
            cmt.delete()
            # redirect to permalink page
            self.redirect('/blog/%d' % int(blog_id))
        else:
            # Action not allowed
            error = "Users can only delete comments they have made."
            comments = Comment.get_comments(blog_post.comments)
            self.render('permalink.html', entry=blog_post,
                    comments=comments, error=error)
