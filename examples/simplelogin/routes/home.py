#-*- coding: utf-8 -*-

"""
    routes.home
    ~~~~~~~~~~~

    Routes related to the homepage.

    :copyright: (c) Authentication Dance by Waltz.
    :license: GPLv3, see LICENSE for more details.
"""

import waltz

class Index:
    """Waltz classes are the same as web.py classes. When a client's
    HTTP request is translated within the urls controller from a regex
    route to the correct class, the class examines the HTTP request
    method type and directs it to its corresponding instance method.

    For example, a GET request to a route which maps to the Index
    class will automatically be handled by a function named GET. The
    same is true about POST, DELETE, and the other HTTP
    methods. Simply create a method with the appropriate name to
    handle that HTTP request type.
    """

    def GET(self):
        """Handles HTTP GET requests to the / route.

        The waltz.render() object is pre-configured to address any file within
        the project's templates/ directory as if it were an instance method.

        Calling waltz.render().filename() will automatically render
        the corresponding templates/filename.html file and inject it
        within the templates/base.html template.

        If using the templates/base.html template is undesirable, an
        alternative render called slender is provided to
        compile/render html files standalone as independent entities.

        For example:
        waltz.slender().index() will render and return
        templates/index.html without first injecting it into
        templates/base.html

        If you would like to create your own custom render object, you
        can do so by accessing the web module via waltz.web and by
        following the web.py documentation.

        See: http://webpy.org/docs/0.3/templetor
        """
        if waltz.session()['logged']:
            return waltz.render().index()
        raise waltz.web.seeother('/login')
