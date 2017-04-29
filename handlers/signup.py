# Signup page
import bloghandler
import utils
from models.user import User


class SignupHandler(bloghandler.Handler):
    """ Signup page handler loads signup HTML template and processes
    user data to create a new User in the registry
    """
    def get(self):
        self.render('signup.html')

    def post(self):
        # Get user input
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        # Process results
        input_error = False
        user_error = ""
        passwd_error = ""
        verify_error = ""
        email_error = ""
        if not utils.valid_username(username):
            user_error = "That's not a valid username"
            input_error = True
        if not utils.valid_password(password):
            passwd_error = "That wasn't a valid password"
            input_error = True
        elif password != verify:
            verify_error = "Your passwords didn't match"
            input_error = True
        if not utils.valid_email(email):
            email_error = "That's not a valid email"
            input_error = True

        # Check if this user is already in our registry
        if not input_error and User.by_name(username):
            user_error = "The user already exists"
            input_error = True

        if not input_error:
            # Create user entry in database
            hashed_pw = utils.make_pw_hash(username, password)
            u = User(name=username, hashed_pw=hashed_pw, email=email)
            u.put()
            # Set cookie to user_id
            uid = u.key().id()
            user_id = utils.make_secure_cookie(str(uid))
            self.response.headers.add_header('Set-Cookie',
                                    'user_id=%s; Path=/' % user_id)
            # Redirect to welcome page
            self.redirect('/blog/welcome')
        else:
            self.render('signup.html', username=username, email=email,
                    user_error=user_error, passwd_error=passwd_error,
                    verify_error=verify_error, email_error=email_error)
