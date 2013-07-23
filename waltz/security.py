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

username_regex = r'([A-Za-z0-9_%s]){%s,%s}$'
passwd_regex = r'([A-Za-z0-9%s]){%s,%s}$'

class Account(object):
    """The base Account class provides the basic functions for allowing
    user account creation and authentication, however it should be
    extended to allow user retrieval.
    """

    @classmethod
    def authenticate(cls, username, passwd, salt, uhash):
        """Authenticates/validates a user's credentials by comparing
        their username and password versus their computed salted hash.
        A successful authentication results in True, False otherwise.
        """
        return cls._roast(username + salt + passwd) == uhash

    @classmethod
    def register(cls, username, passwd, passwd2=None, salt='', email='', **kwargs):
        """Creates a complete user tuple according to seed
        credentials. The input undergoes a salting and roasting during
        a hashing process and all values are returned for further db
        handling (db insertion, etc). Note: For security reasons,
        plaintext passwords are never returned and should not be
        stored in a db unless there's a very specific reason to.

        XXX: Consider adding the following keyword arguments:
        password_validator - lambda for validating passwd (chars, len)
        username_validator - lambda for validating username (len, etc)

        :param salt: used for testing/verifying hash integrity in tests
        :param kwargs: any addt'l info which should be saved w/ the created user

        usage:
        >>> from waltz import Account
        # typically, salt is not provided as an argument and is instead
        # generated as a side effect of Account.register("username", "password").
        # A salt has been included along with the following function call to
        # guarantee idempotence (i.e. a consistent/same uhash with each call)
        >>> Account.register("username", "password", salt="123456789")
        <Storage {'username': 'username', 'uhash': '021d98a32375ed850f459fe484c3ab2e352fc2801ef13eae274103befc9d0274', 'salt': '123456789', 'email': ''}>
        # using additional kwargs, such as age (i.e. age=24) to add user attributes
        >>> Account.register("username", "password", salt="123456789", age=24)
        <Storage {'username': 'username', 'uhash': '021d98a32375ed850f459fe484c3ab2e352fc2801ef13eae274103befc9d0274', 'salt': '123456789', 'email': '', 'age': 24}>
        """        
        if not passwd: raise ValueError('Password Required')

        if email and not valid_email(email):
            raise ValueError("Email '%s' is malformed and does not " \
                                 "pass rfc3696." % email)
        if passwd2 and not passwd == passwd2:
            raise ValueError('Passwords do not match')
        salt = salt or cls._salt()
        uhash = cls._roast(username + salt + passwd)        
        return Storage(zip(('username', 'salt', 'uhash', 'email'), 
                        (username, salt, uhash, email)) + kwargs.items())

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

