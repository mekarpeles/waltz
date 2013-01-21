=====
Waltz
=====

Waltz (v.0.1.62) is a web.py based web framework for rapidly designing
web apps in 3/4 time. Waltz comes pre-configured, ready to run, and
includes features like out-of-the-box support for analytics
tracking. Waltz and never miss a beat.

Installation
============

    pip install waltz

Example
=======

Feel free to clone the following code snippet from https://gist.github.com/4584751.git or wget the raw file from https://gist.github.com/raw/4584751/08ed11e5aa774a3a224f1c3d903562b9f5366775/main.py

Typical usage often looks like this::

    #!/usr/bin/env Python

    import waltz
    from waltz import track, db, render, session

   urls = ('/session', 'Session',
           '/analytics', 'Analytics',
           '/', 'Index')

    sessions = {'cart': waltz.Cart()}
    app = waltz.setup.dancefloor(urls, globals(), sessions=sessions)

    class Index:
        @track
        def GET(self):
            return render().index()

    class Session:
        def GET(self):
            return session()

    class Analytics:
        def GET(self):
            return db.get('analytics')

    if __name__ == "__main__":
        app.run()

TODO
====

* Oauth Integration
* Payment Processing Modules (consider stripe checkout)
