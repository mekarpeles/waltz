#-*- coding: utf-8 -*-

"""
    ballroom.decorations
    ~~~~~~~~~~~~~~~~~~~~
    A collection of route decorators

    :authors Mek
    :license pending
"""

from waltz import web, db
import os
from copy import copy

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
            db().append('analytics', ctx)
            return fn(*args, **kwargs)        
        return inner
    return tracked(fn)

def exponential_backoff(exception, err='expn backing off', tries=5):
    """Decorator @exponential_backoff(Exception, err='', tries=4)"""
    def decorator(func):
        def inner(*args, **kwargs):
            for n in range(0, tries):
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    scalar = random.randint(0, 1000) / 1000.0
                    time.sleep((2 ** n) + scalar)
                    raise exception('%s - %s' % (err, e))
        return inner
    return decorator
