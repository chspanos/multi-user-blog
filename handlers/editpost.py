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
    def get(self):
        # Get post from id
        blog_id = self.get_post_id()
        blog_post = BlogPost.get_by_id(blog_id)
        if blog_post:
            # Check for author of post
            if self.user and blog_post.valid_author(self.user):
                # render the form with the old content inserted
                subject = blog_post.subject
                content = blog_post.content
                self.render('form.html', subject=subject, content=content)
            else:
                # invalid user
                msg = "Users can only edit their own posts"
                comments = Comment.get_comments(blog_post.comments)
                self.render('permalink.html', entry=blog_post,
                        comments=comments, error=msg)
        else:
            # invalid post so redirect to welcome page
            self.redirect('/blog/welcome')

    @decorator.user_logged_in
    def post(self):
        # Get post from id
        blog_id = self.get_post_id()
        blog_post = BlogPost.get_by_id(blog_id)
        if blog_post:
            # Check for author of post
            if self.user and blog_post.valid_author(self.user):
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
            else:
                # User is invalid
                msg = "Users can only edit their own posts"
                comments = Commment.get_comments(blog_post.comments)
                self.render('permalink.html', entry=blog_post,
                        comments=comments, error=msg)
        else:
            # Invalid post so redirect to welcome page
            self.redirect('/blog/welcome')
