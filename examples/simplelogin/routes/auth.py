#-*- coding: utf-8 -*-

"""
    routes.auth
    ~~~~~~~~~~~

    Routes for handling authentication (login, register, logout)

    :copyright: (c) Authentication Dance by Waltz.
    :license: GPLv3, see LICENSE for more details.
"""

import waltz
from waltz import User, web, session, render

class Login:
    def GET(self, msg=""):
        if session()['logged']:
            msg = "Already logged in"
        return render().login(msg=msg)

    def POST(self):        
        i = web.input(email="", password="")
        if not waltz.utils.valid_email(i.email):
            return self.GET(msg="invalid email")
        try:
            u = User(i.email)
        except AttributeError:
            return self.GET(msg="no such user")
        if u.authenticate(i.password):
            session().update({'logged': True,
                              'email': i.email})
            raise web.seeother('/')
        return self.GET(msg="invalid credentials")

class Register:
    def GET(self, msg=""):
        return render().login(msg=msg)

    def POST(self):
        i = web.input(email="", password="", password_confirm="")
        if not waltz.utils.valid_email(i.email):
            return self.GET(msg="invalid email")
        try:
            u = User(i.email)
        except:
            u = User.register(i.email, i.password, passwd2=i.password_confirm)
            session().update({'logged': True,
                              'email': i.email})
            raise web.seeother('/')
        return Login().GET(msg="User already exists")

class Logout:
    def GET(self):
        """Invalidate session, log the user out"""
        i = web.input(redir='/login')
        session().update({'email': None, 'logged': False})
        session().kill()
        raise web.seeother(i.redir)
