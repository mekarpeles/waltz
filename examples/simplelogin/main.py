#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
    main.py
    ~~~~~~~

    Main waltz application.

    :copyright: (c) Authentication Dance by Waltz.
    :license: GPLv3, see LICENSE for more details.
"""

import waltz

# These are web.py url tuples which map a regex url route to the Class
# responsible for implementing its response. In other words, when the
# client issues/submits a HTTP request to the base server
# (e.g. http://example.com/) the response will be returned according
# to the Index class in the file home.py within the routes directory
# (e.g routes.home.Index)
urls = ('/analytics/?', 'waltz.modules.Analytics',
        '/login/?', 'routes.auth.Login',
        '/register/?', 'routes.auth.Register',
        '/logout/?', 'routes.auth.Logout',
        '/?', 'routes.home.Index')

# Default values for a user's session
sessions = {'email': None, 'logged': False}

# These environment variables will be made accessible within the scope
# of html files via the Templator markup language
env = {'split': lambda s, delim: s.split(delim) }

# Setting up and configuring the waltz application. To see all available
# options, refer to waltz/setup.py
app = waltz.setup.dancefloor(urls, globals(), sessions=sessions, env=env)

if __name__ == "__main__":
    app.run()
