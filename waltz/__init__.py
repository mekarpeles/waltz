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
render = lambda: getattr(web.ctx, 'render', None)
slender = lambda: getattr(web.ctx, 'render', None)
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
            return users[uid]
        return users

    @classmethod
    def insert(cls, usr):
        """Appends usr to users in db and returns the
        id of the new user
        """
        users = db().get('users', default={})
        uid = len(users)
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
    def register(cls, username, passwd, passwd2=None, email='',
                 enabled=True, **kwargs):
        """Calls Account's regiser method and then injects **kwargs
        (additional user information) into the resulting dictionary.
        """
        if any(map(lambda usr: usr['username'] == username,
                   cls.get().values())):
            raise Exception("Username already registered")
        usr = super(User, cls).register(username, passwd,
                                        passwd2=passwd2, email=email)
        usr.enabled = enabled
        usr.update(**kwargs)
        return cls.insert(usr)
