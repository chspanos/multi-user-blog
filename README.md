# Multi-User Blog

In this project, I created a multi-user blog application implemented in Python using Google App Engine and Jinja templates.

The blog features a main page that displays the most recent posts. Users must signup to contribute to the blog. Once registered, users can login or logout of the site without have to recreate their account. Stored passwords are hashed and checked during login. User cookies are securely set.

Once signed up, the user is directed to a welcome page that also serves as a control panel. From this welcome page, a user can create, edit, and delete their own blog posts.

The main page displays a list of posts, ordered with the most recent entries at the top. It also contains links to the individual permalink pages for each displayed post. Logged in users can visit these pages to like other people's posts and leave comments. Users can only edit and delete comments that they themselves have made.

### How to run this website

A working version of this website should be available at [https://hello-udacity83.appspot.com/blog](https://hello-udacity83.appspot.com/blog)

Alternatively, you can install Google App Engine SDK and sign up for a Google App Engine Account. Follow their instructions to create your unique appspot.com project site and get a sample app up and running.

To run my application, you will need to download the following files from my github repository:
* `app.yaml` - Configuration information, which tells the Google App Engine where to find the needed files and templates
* `blog.py` - Contains the server-side code to create and launch the website.
* `templates/*.html` - Subdirectory containing 9 HTML templates for the various blog pages.
* `static/css/*.css` - Subdirectory containing the 2 CSS style files needed to format the HTML.

Once all files are downloaded, open your Google Cloud SDK Shell. Go to the directory containing the blog code. Deploy your project with `gcloud app deploy`. Visit your appspot.com site to view your blog.

#### Attributions

This project is part of Udacity's Full Stack Web Developer nanodegree.

For more information on Google App Engine, visit [https://cloud.google.com/appengine/downloads](https://cloud.google.com/appengine/downloads)
