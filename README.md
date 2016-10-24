# Waltz

![Build Status](https://travis-ci.org/mekarpeles/waltz.png)

Waltz is a web.py based web framework for rapidly designing
web apps in 3/4 time. Waltz comes pre-configured, ready to run, and
includes features like out-of-the-box support for analytics
tracking. Waltz and never miss a beat.

- [Installation](#installation)
- [Quickstart](#quickstart)
- [Getting Started](#getting-started)
- [Building your Application](#building-your-application)
- [The Built-in Database](#lazydb)
- [Test](#tests)

## Installation

    $ pip install waltz

### To build from source:

    # Build latest from github
    $ git clone http://github.com/mekarpeles/waltz
    $ cd waltz
    $ pip install .    

## Quickstart

If you don't have time for dance lessons and want to try waltzing, execute the following code at the command line and then navigate to the url localhost:8080 in your favourite web browser:

    $ mkidir project
    $ cd project
    $ waltz init
    $ python main.py 8080

## Getting Started Guide

This section explains what's happening during the Quickstart (above). First, we're creating a directory `project` where our application is going to live:

    $ mkdir project
    $ cd project

Next we are going to setup scaffolding for our application, similar to django or rails. Waltz comes with a command line utility for creating a default/standard waltz application. 

    $ waltz
    usage: waltz [-h] [--name NAME] [init]

    Waltz is a web.py framework for designing web apps in 3/4 time

    positional arguments:
      init         Start a waltz application

    optional arguments:
      -h, --help   show this help message and exit
      --name NAME  Specify a name

We can use 'waltz init' to generate our default application. By default, the application file which is generated will be called 'main.py'. We can provide an optional '--name' flag/argument in order to name this script something different, like core.py. In this example, we'll stick with main.py.

    $ waltz init
    $ ls
    main.py  routes/  static/  subapps/  templates/

You'll notice performing 'waltz init' has resulted in the creation of the scaffolding of our waltz application. Each of these directories, files, and their relationships will be described later. Note: If you accidentally run 'waltz init' multiple times, your main.py and routes/home.py files will be overwritten, however, none of the directories will be overridden if they already existed.

To run our application, we invoke it with python and optionally provide an optional port # argument after the script name. We can add an ampersand to the end of the command to run our website in the background, this way our application can continue to run as we make changes. In debug mode, waltz invokes a PeriodicReloader which automatically reloads your application every time changes are made (without having to restart the application).

    $ python main.py 8080 & # <port> optional, defaults to 8080 if absent

Note: the 'db' file below (a LazyDB flatfile database for storing waltz 'analytics' and 'users' -- both optional) will only exist after you have visited your web application in a browser.

## Building your Application

After running the 'waltz init' command line tool (which generates a file called main.py) and starting your application (running main.py) for the first time, several directories and template files will magically appear (i.e. be created/generated). This step is called 'scaffolding'. Don't worry, 'scaffolding' is smart enough to not replace or overwrite any your existing project files -- it will only create necessary files and or directories which do not already exist. After scaffolding, your project directory will look like this: 

    $ ls
    db  main.py  routes/  sessions/  static/  subapps/  templates/

### main.py

Main.py is the driver / main runnable python program which starts up your waltz application. Within main.py, there are two central components: (1) url route mappings and (2) waltz framework setup and configuration. The default main.py which is created by the 'waltz init' stage looks something like this (a few numbered comments have been added for reference):

    #!/usr/bin/python
    #-*- coding: utf-8 -*-

    import waltz
    from waltz import track, render

    # (1) url route mappings (regex url -> python class)
    urls = ('/analytics/?', 'waltz.modules.Analytics',
            '/?', 'Index')

    # (2) waltz application setup + configuration
    sessions = {}
    env = {}
    app = waltz.setup.dancefloor(urls, globals(), sessions=sessions, env=env)

    # (3) Code to handle HTTP responses to and url mapped to the class Index 
    class Index:
        @track
        def GET(self):
            return render().index()

    if __name__ == "__main__":
        app.run()

#### 1) URL Handling, Routes

http://webpy.org/docs/0.3/tutorial#urlhandling

#### 2) Waltz Setup 

Main.py is used to prime the dancefloor, that is, configure your entire waltz application. This setup includes initializing sessions (ref to: sessions), defining which python functions your html templates will have access to (ref to: env), and configuration details like whether the server should be started in debug mode. 

#### 3) Response Classes

As previously described, the 'urls' variable describes a mapping of urls a client enters in their browser to specific python classes which will handle user requests / server HTTP responses back to the client. These classes implement HTTP methods, such as GET and or POST to render views + data for the client. It is good form to keep this logic (the location/path of the classes reference by the 'urls' variable) within the routes/ directory. If at all possible, you should avoid placing them directly within main.py.

For more information on how these HTTP Response classes work and the differen types of HTTP methods, please refer to http://webpy.org/docs/0.3/tutorial#getpost

### LazyDB

Waltz comes with a ready-to-go built-in flatfile (shelve-based) database called LazyDB which is built to support basic 'user' sessions and service 'analytics' for your project(s). Chances are, we won't need to do anything with this db other than use the waltz apis to interface with it. If we want to manually interface with the db, we can do so with either the LazyDB python module or the shelve python module. 

    $ python
    >>> from lazydb import Db
    >>> db = Db('db')
    >>> db.keys()
    ['analytics']

## Tests

You can run the waltz test by invoking 'nosetests' from the top level waltz directory.
