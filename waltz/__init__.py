#!/usr/bin/env python

"""waltz: make web apps in 3/4 time (http://github.com/mekarpeles/waltz)"""

__version__ = "0.1.71"
__author__ = [
    "Mek <michael.karpeles@gmail.com>"
]
__license__ = "public domain"
__contributors__ = "see AUTHORS"

import logging
import web
from lazydb import Db

def logger(logpath, msg, level=logging.INFO, method='info'):
    logging.basicConfig(filename=logpath, level=level)
    getattr(logging, method, 'info')(msg)

session = lambda: getattr(web.ctx, 'session', None)
# render: renders a template through base template base.html
# (unless base template name is overridden)
render = lambda: getattr(web.ctx, 'render', None)
# slim render: renders a template by itself with no base template
slender = lambda: getattr(web.ctx, 'slender', None)
# db for waltz analytics, etc.
db = lambda: Db(web.ctx['waltz']['db'])
log = lambda msg, lbl='info': logger(web.ctx['waltz']['logging'], msg, method=lbl)

from security import Account
from decorations import *
from utils import *
from treasury import *
from setup import *
from modules import rss
from utils import Storage

class User(Account, Storage):
    """Extends Account to use LazyDB as Datastore"""

    udb = 'users'
    db = staticmethod(db)

    def __init__(self, uid, user=None):
        """
        TODO:
        * Provide ability to self.save()
        * Extend __init__ to populate User obj as Storage
        """
        u = user if user else self.get(uid)
        if u is None:
            raise AttributeError("No user found with id: %s" % uid)
        for k, v in u.items():
            setattr(self, k, v)


    def __repr__(self):     
        return '<User ' + repr(self._publishable(dict(self))) + '>'

    def save(self):
        """save the state of the current user in the db; replace
        existing databased user (if it exists) with this instance of
        the User or insert this User otherwise
        """
        users = User.getall()
        users[self.username] = dict(self)
        return self.db().put(self.udb, users)

    @classmethod
    def getall(cls, safe=False):
        users = cls.db().get(cls.udb, default={}, touch=True)
        for uid, user in users.items():           
            u = (user if not safe else cls._publishable(user))
            users[uid] = cls(uid, user=u)
        return users

    @classmethod
    def get(cls, uid, safe=False):
        """
        params:
            uid - the user id which to fetch
            safe - return users without secure fields like salt and hash
            db - provide your own instantiated lazydb.Db() connector
        """
        if uid is not None:
            users = cls.getall()
            try:
                return users[uid] if not safe else cls._publishable(users[uid])
            except KeyError:
                return None

    @classmethod
    def _publishable(cls, usr, *args):
        """Make this user publishable. Removes fields from a user
        which would be undesirable to publish publicly, like salt or
        hash. Can take an arbitrary list of additional keys to
        scrub/remove"""
        keys = set(args + ('uhash', 'salt'))
        for key in keys:
            if key in usr:
                del usr[key]
        return usr

    @classmethod
    def insert(cls, usr, pkey='username'):
        """Appends usr to users in db and returns the
        id of the new user.
        
        params:
            usr - dictionary or Storage
        """
        users = cls.db().get(cls.udb, default={}, touch=True)
        uid = usr[pkey]
        users[uid] = usr
        users = cls.db().put(cls.udb, users)
        return uid

    @classmethod
    def replace(cls, uid, usr):
        users = cls.db().get(cls.udb, {}, touch=True)
        users[uid] = usr
        cls.db().put(cls.udb, users)
        return usr

    @classmethod
    def update(cls, uid, func=lambda x: x):
        """Updates a given user by applying a func to it. Defaults to
        identity function
        """
        users = cls.db().get(cls.udb, default={}, touch=True)
        user = func(users[uid])
        users[uid] = user
        cls.db().put('users', users)
        return user

    @classmethod
    def delete(cls, uid):
        users = cls.db().get(cls.udb, default={}, touch=True)
        try:
            del users[uid]
            return cls.db().put(cls.udb, users)
        except KeyError:
            return False

    def authenticate(self, passwd):
        """Instance level authentication for a User

        usage:
        >>> u = User('username')
        >>> u.authenticate('password')
        True
        """
        return self.easyauth(dict(self), passwd)

    @classmethod
    def easyauth(cls, u, passwd):
        """New-style auth which takes a user dict and a passwd

        params:
            u - a user dict with (at least) items:
                ['salt', 'uhash', 'username']
        """
        if u and all(key in u for key in ['username', 'salt', 'uhash']):
            return Account.authenticate(u['username'], passwd,
                                        u['salt'], u['uhash'])
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
        <Storage {'username': 'username',
        'uhash': '021d98a32375ed850f459fe484c3ab2e352fc2801ef13eae274103befc9d0274', 
        'salt': '123456789', 'email': 'username@domain.org'}>
        """
        #if not cls.registered(username):
        user = super(User, cls).register(username, passwd, passwd2=passwd2,
                                         email=email, salt=salt, **kwargs)
        user.enabled = enabled
        uid = cls.insert(user, pkey=pkey)
        return cls(user.username, user=user)

    @classmethod
    def registered(cls, username):
        """predicate which answers whether a username exists in the User db.

        XXX registered() should be made more flexible to accomomdate
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
        if any(usr['username'] == username for usr in cls.getall().values()):
            return True
        return False

    @classmethod
    def change_db(cls, dbname):
        """Internally sets the name of the database to use"""
        setattr(cls, 'db', staticmethod(lambda: Db(dbname)))
