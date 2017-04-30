# Edit comment page handler
import bloghandler
import decorator
from models.post import BlogPost
from models.comment import Comment


class EditComment(bloghandler.Handler):
    """ EditComment handler reloads the comment HTML template with the
    current comment text and allows its User author to edit it.
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
            self.render('comment.html', entry=blog_post,
                        comment=cmt.text)
        else:
            msg = "Users can only edit comments they themselves have made."
            comments = Comment.get_comments(blog_post.comments)
            self.render('permalink.html', entry=blog_post,
                    comments=comments, error=msg)

    @decorator.user_logged_in
    @decorator.post_exists
    def post(self, blog_id):
        # Get post from id
        blog_post = BlogPost.get_by_id(int(blog_id))
        # Get comment from id
        cid = self.request.get('cid')
        cmt = self.get_valid_comment(cid)
        # Check user
        if blog_post and cmt and cmt.valid_author(self.user):
            # Get action
            action = self.request.get('action')
            if action and action == 'Save':
                # get new comment
                cmt_text = self.request.get('comment')
                if cmt_text:
                    # Udpate comment with new content
                    cmt.update_text(cmt_text)
                    cmt.put()
                    # Redirect to permalink page
                    self.redirect('/blog/%d' % int(blog_id))
                else:
                    # Error, so return to form
                    error = "Please enter a comment"
                    self.render('comment.html', entry=blog_post,
                        error=error)
            else:
                # Cancel the edit and redirect to permalink page
                self.redirect('/blog/%d' % int(blog_id))
        else:
            # Cancel the edit and redirect to permalink page
            self.redirect('/blog/%d' % int(blog_id))
