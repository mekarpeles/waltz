#-*- coding: utf-8 -*-

"""
    security
    ~~~~~~~~
    Generic User class for interfacing with use accounts +
    authentication.
"""

import hashlib
import random
from utils import Storage, to36, valid_email, \
    ALPHANUMERICS as ALPHAS

class User(object):
    """The base User class provides the basic functions for allowing
    user account creation and authentication, however it should be
    extended to allow user retrieval.
    """
    def __init__(self, uid):
        """Should be extended to retrieve a User by id"""
        self.public_id = to36(uid)
        self.id = uid

    @classmethod
    def query(cls, **kwargs):
        """Override this placeholder function to query in your super
        user class.
        """
        pass

    @classmethod
    def authenticate(cls, username, passwd, salt, uhash):
        """Authenticates/validates a user's credentials by comparing
        their username and password versus their computed salted hash.
        A successful authentication results in True, False otherwise.
        """
        if cls._roast(username + salt + passwd) == uhash:
            return True
        return False

    @classmethod
    def register(cls, username, passwd, passwd2=None, email=''):
        """Creates a complete user tuple according to seed
        credentials. The input undergoes a salting and roasting during
        a hashing process and all values are returned for further db
        handling (db insertion, etc). Note: For security reasons,
        plaintext passwords are never returned and should not be
        stored in a db unless there's a very specific reason to.

        XXXX Consider taking **kwargs:
            password_validator - lambda for validating passwd (chars, len)
            username_validator - lambda for validating username (len, etc)
        """
        
        if not passwd: raise ValueError('Password Required')
        if not passwd: raise ValueError('Password Required')

        if email and not valid_email(email):
            raise ValueError("Email '%s' is malformed and does not " \
                                 "pass rfc3696." % email)
        if passwd2 and not passwd == passwd2:
            raise ValueError('Passwords do not match')
        salt = cls._salt()
        uhash = cls._roast(username + salt + passwd)        
        return Storage(zip(('name', 'salt', 'uhash', 'email'), 
                        (username, salt, uhash, email)))

    @classmethod
    def public_key(cls, uid, username, salt):
        """Generates a public key which can be used as a public unique
        identifier token in account activation emails and other
        account specific situations where you wish to create a url
        intended to only work for a specific user.
        """
        return cls._roast(uid + username + salt)

    @classmethod
    def _salt(cls, length=12):
        """http://en.wikipedia.org/wiki/Salt_(cryptography)
        Salting results in the generation of random padding of a
        specified 'length' (12 default) which can be prepended or
        appended to a password prior to hashing to increase security
        and prevent against various brute force attacks, such as
        rainbow-table lookups."""
        return ''.join([random.choice(ALPHAS) for i in range(length)])

    @classmethod
    def _roast(cls, beans, chash=hashlib.sha256):
        """Computes a hash digest from username, salt, and
        password. Hot swappable algo in case there are code changes
        down the road."""
        return chash(beans).hexdigest()

