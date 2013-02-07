#!/usr/bin/env python

"""waltz: make web apps in 3/4 time (http://github.com/mekarpeles/waltz)"""

__version__ = "0.1.62"
__author__ = [
    "Mek <michael.karpeles@gmail.com>"
]
__license__ = "public domain"
__contributors__ = "see AUTHORS"

import web

session = lambda: getattr(web.ctx, 'session', None)
# render: renders a template through base template base.html
# (unless base template name is overridden)
render = lambda: getattr(web.ctx, 'render', None)
# slim render: renders a template by itself with no base template
slender = lambda: getattr(web.ctx, 'render', None)
# db for waltz analytics, etc.
db = lambda: Db(web.ctx['waltz']['db'])

from security import Account
from decorations import *
from utils import *
from treasury import *
from setup import *

class User(Account):
    """Extends Account to use LazyDB as Datastore"""
    def __init__(self, uid):
        super(User, self).__init__(uid)

    @classmethod
    def get(cls, uid=None):
        users = db().get('users', {})
        if uid:
            try:
                return users[uid]
            except:
                return None
        return users

    @classmethod
    def insert(cls, usr, pkey='username'):
        """Appends usr to users in db and returns the
        id of the new user.
        
        params:
            usr - dictionary or Storage
        """
        users = db().get('users', default={})
        uid = usr[pkey]
        users[uid] = usr
        users = db().put('users', users)
        return uid

    @classmethod
    def update(cls, uid, func=lambda x: x):
        """Updates a given user by applying a func to it. Defaults to
        identity function
        """
        users = db().get('users', {})
        user = func(users[uid])
        users[uid] = user
        return user

    @classmethod
    def easyauth(cls, u, passwd):
        """New-style auth which takes a user dict and a passwd

        params:
            u - a user dict with (at least) items:
                ['salt', 'uhash', 'username']
        """
        if u and all(key in ['username', 'salt', 'uhash'] for key in u):
            return cls.authenticate(u['username'], passwd, # user provided
                                    u['salt'], u['uhash']) # db provided
        raise TypeError("Account._auth expects user object 'u' with " \
                            "keys: ['salt', 'uhash', 'username']. " \
                            "One or more items missing from user dict u.")

    @classmethod
    def register(cls, username, passwd, passwd2=None, email='',
                 enabled=True, pkey="username", **kwargs):
        """Calls Account's regiser method and then injects **kwargs
        (additional user information) into the resulting dictionary.
        
        XXX Additional constraints required (like check for multiple
        emails + other keys which should be 'unique')
        """
        if any(map(lambda usr: usr['username'] == username,
                   cls.get())):
            raise Exception("Username already registered")
        usr = super(User, cls).register(username, passwd,
                                        passwd2=passwd2, email=email)
        usr.enabled = enabled
        usr.update(**kwargs)
        uid = cls.insert(usr, pkey=pkey)
        return usr
