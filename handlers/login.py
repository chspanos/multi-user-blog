# Login page
import bloghandler
import utils
from models.user import User


class LoginHandler(bloghandler.Handler):
    """ Login page handler loads login HTML template and processes user
    data to retrieve an existing User from the registry.
    """
    def get(self):
        self.render('login.html')

    def post(self):
        # Get user input
        username = self.request.get('username')
        password = self.request.get('password')
        # Check if user is in database
        u = User.by_name(username)
        if u and utils.valid_pw(username, password, u.hashed_pw):
            # Process a valid input
            # Set cookie to user_id
            uid = u.key().id()
            user_id = utils.make_secure_cookie(str(uid))
            self.response.headers.add_header('Set-Cookie',
                                    'user_id=%s; Path=/' % user_id)
            # Redirect to welcome page
            self.redirect('/blog/welcome')
        else:
            # error
            error_msg = "Invalid username or password"
            self.render('login.html', error_msg=error_msg)
