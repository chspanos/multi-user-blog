# Like post handler
import bloghandler
import decorator
from models.post import BlogPost
from models.comment import Comment

class LikeHandler(bloghandler.Handler):
    """ Like handler processes a user request to "like" a blog post """
    @decorator.user_logged_in
    @decorator.post_exists
    def get(self, blog_id):
        # get blog entry
        entry = BlogPost.get_by_id(int(blog_id))
        # get user id
        uid = self.user and self.user.key().id()
        # Check if this user is allowed to like this post
        if entry.valid_author(self.user):
            error = "Authors aren't permitted to like their own posts"
            comments = Comment.get_comments(entry.comments)
            self.render('permalink.html', entry=entry,
                    comments=comments, error=error)
        elif entry.user_already_liked(uid):
            error = "Users are only permitted to like a post once"
            comments = Comment.get_comments(entry.comments)
            self.render('permalink.html', entry=entry,
                    comments=comments, error=error)
        else:
            # like the post
            entry.add_like(uid)
            entry.put()
            self.redirect('/blog/%d' % int(blog_id))
