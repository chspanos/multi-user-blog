# New comment page
import bloghandler
import decorator
from models.post import BlogPost
from models.comment import Comment


class NewComment(bloghandler.Handler):
    """ New Comment handler loads the comment HTML template and
    processes user input to create a new comment. The new comment is
    added to the Comment database and linked with the blog post.
    """
    @decorator.user_logged_in
    @decorator.post_exists
    def get(self, blog_id):
        # Get post from id
        blog_post = BlogPost.get_by_id(int(blog_id))
        self.render('comment.html', entry=blog_post)

    @decorator.user_logged_in
    @decorator.post_exists
    def post(self, blog_id):
        # Get post from id
        blog_post = BlogPost.get_by_id(int(blog_id))
        # Get action
        action = self.request.get('action')
        if action and action == 'Save':
            # get comment text
            cmt_text = self.request.get('comment')
            if cmt_text:
                # Create new Comment object
                c = Comment(blog_post=blog_post, author=self.user,
                            text=cmt_text)
                c.put()
                # Add comment to blog_post
                cid = c.key().id()
                blog_post.add_comment(cid)
                blog_post.put()
                # Redirect to permalink page
                self.redirect('/blog/%d' % int(blog_id))
            else:
                # Error, so return to form
                error = "Please enter a comment"
                self.render('comment.html', entry=blog_post, error=error)
        else:
            # Cancel the edit and redirect to permalink page
            self.redirect('/blog/%d' % int(blog_id))
