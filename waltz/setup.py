#-*- coding: utf-8 -*-

"""
    ballroom.setup
    ~~~~~~~~~~~~~~
    Setup webpy app with additional waltz;
    Sessions and authentication, templates, etc.

    :copyright: (c) 2012 by Mek
    :license: BSD, see LICENSE for more details.
"""

import os
from functools import partial
import web
from web import wsgiserver
from reloader import PeriodicReloader
_https = wsgiserver.CherryPyWSGIServer

def dancefloor(urls, fvars, sessions=False, autoreload=False,
               debug=True, **kwargs):
    """
    params:
        urls - a flat tuple consisting of alternating strings pairs
               representing a mapping between a route's regex match
               and its handling Class ("/route-regex", "ClassHander", ...)
        fvars - globals() containing __file__ or __main__ sent from
                root main.py app
        sessions - a boolean False denotes sessions will not be used.
                   Otherwise, a dict is expected which is used as
                   the default session data structure / values.
    **kwargs:
        env - a dict of environment ctx vars + funcs which will
              be made globally accesible from within html templates
        session_store - can be overridden with a web.session storage
                        method s.t. the user may use DBStore or specify
                        an alternate path besides the default, 'sessions/'
        session - a dictionary representing a default init'd session
    """
    _path = os.path.dirname(os.path.realpath(fvars['__file__']))
    app = web.application(_preprocess(urls), fvars, autoreload=autoreload)
    env = {'ctx': web.ctx}
    env.update(kwargs.get('env', {}))

    if isinstance((kwargs.get('ssl', None)), tuple):        
        _https.ssl_certificate, _https.ssl_private_key = kwargs.get('ssl')

    def setup_rendering():
        html = partial(web.template.render, '%s/templates/' % _path)
        slender = html(globals=env)
        render = html(base='base', globals=env)
        def render_hook():
            web.ctx.render = render
            web.ctx.slender = slender
        app.add_processor(web.loadhook(render_hook))
        env['render'] = slender

    def setup_sessions():
        if sessions is False:
            env['session'] = None
            return
        def default_store():
            """Default method of storing session: DiskStore
            created directory sessions/ by default to store sessions"""
            path = _path + '/sessions'
            if not os.path.exists(path):
                os.makedirs(path)
            return web.session.DiskStore(path)

        store = kwargs.get('session_store', default_store())
        session = init_sessions(web, app, store, sessions)
        env['session'] = session

    def setup_waltz():
        def fcgi(func, addr=None):
            """nginx with spawn-fcgi"""
            return web.wsgi.runfcgi(func, addr)
        web.config.debug = debug
        if debug:
            PeriodicReloader()
        if kwargs.get('fcgi'):
            web.wsgi.runwsgi = fcgi
        db = kwargs.get('db', "%s/db" % _path)
        lgr = kwargs.get('logging', '%s/events.log' % _path)
        def waltz_hook():
            web.ctx.waltz = {"debug": debug,
                             "db": db,
                             "logging": lgr
                             }
        app.add_processor(web.loadhook(waltz_hook))        

    setup_rendering()
    setup_sessions()
    setup_waltz()
    return app

def init_sessions(web, app, store, session):
    """kwargs is used to inject options like 'cart' into session."""
    web.config.session_parameters['ignore_expiry'] = True
    session = web.session.Session(app, store, initializer=session)
    def inject_session():
        """closure; uncalled function which wraps session is
        passed to the web loadhook and invoked elsewhere and at a
        later point in time
        """
        web.ctx.session = session
    app.add_processor(web.loadhook(inject_session))
    return session

def init_scaffolding(_path, appname="main.py", **kwargs):
    """Builds scaffolding for the project:
    static/, templates/, routes/, subapps/"""

    def build_static():
        """Builds a static/ directory within the project
        with subdirs: static/css, static/js, and static/imgs"""
        from waltz.static import style
        path = _path + '/static'
        if not os.path.exists(path):
            os.makedirs(path)
        for subdir in ['css', 'js', 'imgs']:
            subpath = '%s/%s' % (path, subdir)
            if not os.path.exists(subpath):
                os.makedirs(subpath)
        stylecss = path + "/css/style.css"
        if not os.path.exists(stylecss):
            with open(stylecss, 'w') as f:
                f.write(style)

    def build_routes():
        """Creates directories + __init__ files for route logic"""
        for d in ['routes', 'subapps', 'test']:
            path = '%s/%s' % (_path, d)
            if not os.path.exists(path):
                os.makedirs(path)
                fname = '%s/%s' % (path, '__init__.py')
                with open(fname, 'w') as f: f.close()

    def build_templates():
        """Builds the templates/ directory"""
        from waltz.static import base, index
        path = '%s/templates' % _path
        if not os.path.exists(path):
            os.makedirs(path)
        for fname, content in [('base', base), ('index', index)]:
            base = '%s/%s.html' % (path, fname)
            if not os.path.exists(base): 
                with open(base, 'w') as f:
                    f.write(content)
    
    def build_app(appname):
        from waltz.static import mainpy, homepy
        appname += ".py" if appname[-3:] != ".py" else ""
        homepypath = '%s/routes/home.py' % _path
        mainpypath = '%s/%s' % (_path, appname)
        for fname, content in [(mainpypath, mainpy),
                               (homepypath, homepy)]:
            if not os.path.exists(fname): 
                with open(fname, 'w') as f:
                    f.write(content)            

    build_static()
    build_routes()
    build_templates()
    build_app(appname)

def _preprocess(urls):
    """Can be used to inject routes in the future"""
    return urls

