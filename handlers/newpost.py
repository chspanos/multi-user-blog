# New blog post entry page
import bloghandler
import decorator
from models.post import BlogPost


class NewPost(bloghandler.Handler):
    """ NewPost page handler loads the form HTML template and processes
    User input to create a new blog post and add it to the database.
    """
    @decorator.user_logged_in
    def get(self):
        self.render('form.html')

    @decorator.user_logged_in
    def post(self):
        # Get action
        action = self.request.get('action')
        if action and action == 'Save':
            subject = self.request.get('subject')
            content = self.request.get('content')
            # Error checking on input
            if subject and content:
                # Create new Blog Post
                b = BlogPost(author=self.user, subject=subject,
                            content=content)
                b.put()
                # Redirect to permalink page
                blog_id = b.key().id()
                self.redirect('/blog/%d' % blog_id)
            else:
                # Error, so return to form
                error = "Please enter subject and content"
                self.render('form.html', subject=subject, content=content,
                            error=error)
        else:
            # Cancel the post and redirect to welcome page
            self.redirect('/blog/welcome')
