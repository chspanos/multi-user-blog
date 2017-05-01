# Multi-User Blog

In this project, I created a multi-user blog application implemented in Python using Google App Engine and Jinja templates.

Some implementation details:
* The user and blog post data are implemented with Python classes. They are  stored using Google App Engine's datastore and accessed with its query methods.
* HTML pages are created using the [Jinja](http://jinja.pocoo.org/) template library. Jinja is a Python library that allows you to insert Python code in the html to enter data and build complex web pages.
* Stored passwords are hashed and checked during login.
* User cookies are securely set and tested to check permissions when editing/deleting blog posts, liking posts, and editing/deleting comments.
* Separate page handlers are implemented for each type of action and bundled in a Python package
* Decorator functions are used in the handlers to validate permissions, such as checking for logged in users, post existence, and valid post ownership.

### Using the Blog

This blog features a main page that displays the most recent posts. Users must signup to contribute to the blog. Once registered, users can login or logout of the site without have to recreate their accounts.

Once signed up, the user is directed to a welcome page that also serves as a control panel. From this welcome page, users can create, edit, and delete their own blog posts.

The main page displays a list of posts, ordered with the most recent entries at the top. It also contains links to the individual permalink pages for each displayed post. Logged in users can visit these pages to like other people's posts and leave comments. Users can only edit and delete comments that they themselves have made.

### How to run this website

A working version of this website should be available at [https://hello-udacity83.appspot.com/blog](https://hello-udacity83.appspot.com/blog)

Alternatively, you can download my code to create your own version of the site. To do this, you will first need to install Google App Engine SDK (select the Python version). See the next section for further information on how to create your unique appspot.com project site and get a sample app up and running.

To run my application, you will also need to download the following files from my github repository:
* `app.yaml` - Configuration information, which tells the Google App Engine where to find the needed files and templates
* `index.yaml` - File used by the datastore to create indexes for queries
* `blog.py` - Contains the server-side code to launch the website
* `utils.py` - Contains helper functions for hashing passwords and creating cookies. **Note:** You will want to modify the `SECRET` string and store it separately.
* `models/*.py` - Python package containing the model classes for our `User`, `BlogPost`, and `Comment` databases
* `handlers/*.py` - Python package containing all the handlers for the individual blog pages
* `templates/*.html` - Subdirectory containing the HTML templates for the various blog pages
* `static/css/*.css` - Subdirectory containing the CSS style files needed to format the HTML

Once all files are downloaded, open your Google Cloud SDK Shell. Go to the directory containing the blog code. Deploy your project with `gcloud app deploy index.yaml`. Visit your appspot.com site to view your blog.

### How to setup Google App Engine

* [Install Python](https://www.python.org/downloads) if necessary (We used version 2.7)
* [Install Google App Engine](https://www.cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python)
* Sign Up for a [Google App Engine account](https://www.console.cloud.google.com/appengine/)
* Create a new project in [Google's Developer Console](https://www.console.cloud.google.com) using a unique name
* Follow the [App Engine Quickstart](https://www.cloud.google.com/appengine/docs/standard/python/quickstart) to get a sample up and running
* Deploy your project with `gcloud app deploy`
* View your project at your-unique-name.appspot.com
* If successful, you should see "Hello World!"
* When developing locally, you can use `dev_appserver.py` to run a copy of your app on your own computer at [http://localhost:8080](http://localhost:8080)

#### Attributions

This project is part of Udacity's Full Stack Web Developer nanodegree.

For more information on Google App Engine, check out the documentation at  [https://cloud.google.com/appengine/docs/](https://cloud.google.com/appengine/docs/).

For further information on Jinja, check out the documentation at [http://jinja.pocoo.org/](http://jinja.pocoo.org/).
