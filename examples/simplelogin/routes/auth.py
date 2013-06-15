#-*- coding: utf-8 -*-

"""
    routes.auth
    ~~~~~~~~~~~

    Routes for handling authentication (login, register, logout)

    :copyright: (c) Authentication Dance by Waltz.
    :license: GPLv3, see LICENSE for more details.
"""

from waltz import User, web, session, render

class Register:
    def POST(self):
        raise NotImplementedError("TODO")

class Login:
    def GET(self):
        return render().login()

    def POST(self):        
        raise NotImplementedError("TODO")

class Logout:
    def GET(self):
        """Invalidate session, log the user out"""
        i = web.input(redir='/login')
        session().update({'email': None, 'logged': False})
        session().kill()
        raise web.seeother(i.redir)
