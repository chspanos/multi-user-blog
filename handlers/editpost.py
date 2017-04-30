# Edit blog post page
import bloghandler
import decorator
from models.post import BlogPost
from models.comment import Comment


class EditPost(bloghandler.Handler):
    """ EditPost handler reloads the form HTML template with the contents
    of a previous blog post entry and allows the User to edit its contents.
    """
    @decorator.user_logged_in
    @decorator.post_exists2
    @decorator.user_owns_post
    def get(self):
        # Get post from id
        blog_id = self.get_post_id()
        blog_post = BlogPost.get_by_id(blog_id)
        # render the form with the old content inserted
        subject = blog_post.subject
        content = blog_post.content
        self.render('form.html', subject=subject, content=content)

    @decorator.user_logged_in
    @decorator.post_exists2
    @decorator.user_owns_post
    def post(self):
        # Get post from id
        blog_id = self.get_post_id()
        blog_post = BlogPost.get_by_id(blog_id)
        # Get action
        action = self.request.get('action')
        if action and action == 'Save':
            # Update content
            subject = self.request.get('subject')
            content = self.request.get('content')
            # Error checking on input
            if subject and content:
                # Update existing Blog Post
                blog_post.update_post_content(subject, content)
                blog_post.put()
                # Redirect to permalink page
                self.redirect('/blog/%d' % blog_id)
            else:
                # Error, so return to form
                error = "Please enter subject and content"
                self.render('form.html', subject=subject,
                    content=content, error=error)
        else:
            # Cancel the edit and redirect to permalink page
            self.redirect('/blog/%d' % blog_id)
