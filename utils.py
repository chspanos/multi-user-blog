# Various helper functions needed for our blog
import re
import random
import string
import hashlib
import hmac


# Helper functions for verifying signup and login input
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASSWD_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASSWD_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_email(email):
    return not email or EMAIL_RE.match(email)


# Helper functions for hashing passwords
def make_salt():
    return ''.join(random.choice(string.letters) for x in range(5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
    salt = h.split(',')[1]
    return h == make_pw_hash(name, pw, salt)


# Helper functions for creating cookies
SECRET = 'Really, really, super secret string'

def make_secure_cookie(s):
    hash_str = hmac.new(SECRET, s).hexdigest()
    return '%s|%s' % (s, hash_str)

def check_secure_cookie(h):
    val = h.split('|')[0]
    if h == make_secure_cookie(val):
        return val
