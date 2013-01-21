Waltz
=====

Waltz (v.0.1.6) is a web.py based web framework for rapidly designing
web apps in 3/4 time. Waltz comes pre-configured, ready to run, and
includes features like out-of-the-box support for analytics
tracking. Waltz and never miss a beat.

Installation
------------

    pip install waltz

Example
-------

    import waltz

    urls = ('/', 'Index')

    app = waltz.setup.dancefloor(urls, globals(), sessions={},  scaffold=True)
    
    class Index:
        def GET(self):
	    return "hello world"

    if __name__ == "__main__":
        app.run()

TODO
----

* Oauth Integration
* Payment Processing Modules (consider stripe checkout)