# Logout page
import bloghandler


class LogoutHandler(bloghandler.Handler):
    """ Logout handler to sign a registered User out of the blog """
    def get(self):
        # Clear cookies
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        # Redirect to signup
        self.redirect('/blog/signup')
