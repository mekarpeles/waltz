#-*- coding: utf-8 -*-

"""
    ballroom.decorations
    ~~~~~~~~~~~~~~~~~~~~
    A collection of route decorators

    :authors Mek
    :license pending
"""

from waltz import web
import os
import random
import time
from copy import copy
from lazydb import Db

def track(fn):
    """A decorator which wraps each route with analytics tracking."""
    def tracked(fn):
        """This setup w/ second inner function allows support for
        passing @track optional arguments and parameters, as well as
        allows for the special case of class methods which require
        self - methods(self).
        """        
        def inner(*args, **kwargs):
            """Copy web context environment, clean it to avoid
            pickeling issues, and dump it to lazydb before returning
            the route
            """
            ctx = copy(web.ctx['env'])
            del ctx['wsgi.errors']
            del ctx['wsgi.input']
            Db(web.ctx['waltz']['db']).append('analytics', ctx)
            return fn(*args, **kwargs)        
        return inner
    return tracked(fn)

def exponential_backoff(exception, err=None, tries=5, debug=False):
    """Exponentially backoff on a certain Exception exception.
    params:
        tries - num of expn backed off attempts before quitting
        err - custom error msg to display in addition to 'e'
              q: are there any reasons why we wouldn't just want
                 to display 'e'? Securiy reasons seem likely.

    note:
        * debug flag used to avoid raising security
          sensitive exception err msgs     
        * sleep may be unsafe (hence adding a psuedo random
          scalar, still bad since not really random)
        * Consider logging errors via
          http://pypi.python.org/pypi/sentry

    usage:
    >>> @exponential_backoff(SomeNetworkError, tries=2)
    ... def foo(bar):
    ...     transfer_file(bar)
    SomeNetworkError: [ExponentialBackoff] Timed out
    after 2 attempts. Network failed to connect. (details: None)
    """
    def decorator(func):
        def inner(*args, **kwargs):
            for n in range(0, tries):
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    scalar = random.randint(0, 1000) / 1000.0
                    time.sleep((2 ** n) + scalar)
            e = e if debug else ''
            raise exception('[Exponential Backoff] ' \
                                'Timed out after %s attempts. ' \
                                '%s (details: %s)' % (tries, e, err))
        return inner
    return decorator
