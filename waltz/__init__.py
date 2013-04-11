#!/usr/bin/env python

"""waltz: make web apps in 3/4 time (http://github.com/mekarpeles/waltz)"""

__version__ = "0.1.66"
__author__ = [
    "Mek <michael.karpeles@gmail.com>"
]
__license__ = "public domain"
__contributors__ = "see AUTHORS"

import web
from lazydb import Db

session = lambda: getattr(web.ctx, 'session', None)
# render: renders a template through base template base.html
# (unless base template name is overridden)
render = lambda: getattr(web.ctx, 'render', None)
# slim render: renders a template by itself with no base template
slender = lambda: getattr(web.ctx, 'slender', None)
# db for waltz analytics, etc.
db = lambda: Db(web.ctx['waltz']['db'])

from security import Account
from decorations import *
from utils import *
from treasury import *
from setup import *
from modules import rss
from utils import Storage

class User(Storage, Account):
    """Extends Account to use LazyDB as Datastore"""

    def __init__(self, uid):
        """
        TODO:
        * Provide ability to self.save()
        * Extend __init__ to populate User obj as Storage
        """
        for k, v in self.get(uid).items():
            setattr(self, k, v)

    def __repr__(self):     
        return '<User ' + dict.__repr__(self) + '>'

    def save(self):
        """save the state of the current user in the db; replace
        existing databased user (if it exists) with this instance of
        the User or insert this User otherwise
        """
        pass

    @classmethod
    def getall(cls, db=db, safe=False):
        users = db().get('users', default={})
        if safe:
            for user in users:
                users[user] = cls._publishable(users[user])
        return users

    @classmethod
    def get(cls, uid=None, safe=False, db=db):
        """
        params:
            uid - the user id which to fetch
            safe - return users without secure fields like salt and hash
            db - provide your own instantiated lazydb.Db() connector
        """
        def _db():
            return db if type(db) is Db else db()
            
        if uid:
            users = cls.getall(db=db)
            #try:
            user = users[uid]
            if safe:
                user = cls._publishable(user)
            return user
            #except:
            #    return None
        return cls.getall(db=db, safe=safe)

    @classmethod
    def _publishable(cls, usr, *args):
        """Make this user publishable. Removes fields from a user
        which would be undesirable to publish publicly, like salt or
        hash. Can take an arbitrary list of additional keys to
        scrub/remove"""
        keys = set(args + ('uhash', 'salt'))
        for key in keys:
            del usr[key]
        return usr

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
    def replace(cls, uid, usr):
        users = db().get('users', {})
        users[uid] = usr
        db().put('users', users)
        return usr

    @classmethod
    def update(cls, uid, func=lambda x: x):
        """Updates a given user by applying a func to it. Defaults to
        identity function
        """
        users = db().get('users', {})
        user = func(users[uid])
        users[uid] = user
        db().put('users', users)
        return user

    @classmethod
    def delete(cls, uid):
        users = db().get('users', {})
        try:
            del users[uid]
            return db().put('users', users)
        except KeyError:
            return False

    @classmethod
    def easyauth(cls, u, passwd):
        """New-style auth which takes a user dict and a passwd

        params:
            u - a user dict with (at least) items:
                ['salt', 'uhash', 'username']
        """
        if u and all(key in u for key in ['username', 'salt', 'uhash']):
            return cls.authenticate(u['username'], passwd, # user provided
                                    u['salt'], u['uhash']) # db provided
        raise TypeError("Account._auth expects user object 'u' with " \
                            "keys: ['salt', 'uhash', 'username']. " \
                            "One or more items missing from user dict u.")

    @classmethod
    def register(cls, username, passwd, passwd2=None, email='', salt='',
                 enabled=True, pkey="username", **kwargs):
        """Calls Account's regiser method and then injects **kwargs
        (additional user information) into the resulting dictionary.
        
        XXX Additional constraints required (like check for multiple
        emails + other keys which should be 'unique')

        :param pkey: the string name of the key which will be used as
                     a primary key for storing/referencing/indexing
                     this user within lazydb
        usage:
        >>> from waltz import User
        >>> User.register("username", "password", passwd2="password",
        ...               email="username@domain.org", salt='123456789',
        ...               pkey="email")
        <Storage {'username': 'username', 'uhash': '021d98a32375ed850f459fe484c3ab2e352fc2801ef13eae274103befc9d0274', 'salt': '123456789', 'email': 'username@domain.org'}>
        """
        def check_registered(username):
            if any(map(lambda usr: usr['username'] == username,
                       cls.get().values())):
                raise Exception("Username already registered")
        
        user = super(User, cls).register(username, passwd, passwd2=passwd2,
                                         email=email, salt=salt, **kwargs)
        user.enabled = enabled
        uid = cls.insert(user, pkey=pkey)
        return user

    @classmethod
    def registered(username):
        """predicate which answers whether a username exists in the User db.

        XXX registered() should be made more flexible to accomodate
        for keys other than username in the case where there are
        UNIQUEness constraints on user attributes, such as email. This
        may mean providing **kwargs of unique User attributes and
        values and iterating over each user in the Db (this linear
        approach is a caveat of lazydb) to ensure UNIQUEness.

        >>> from waltz import User
        >>> User.registered("username")
        True
        >>> User.registered("Guido van Rossum")
        False
        """
        pass
