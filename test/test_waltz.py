#-*- coding: utf-8 -*-

"""
    waltz.test
    ~~~~~~~~~~

    Test cases for the waltz web framework. Test cases follow webpy's
    test documentation documented here:
    http://webpy.org/cookbook/testing_with_paste_and_nose    
"""

import unittest
import os
import shutil
from paste.fixture import TestApp
import waltz
from waltz import Account, User, web, storage

USERNAME = "username"
PASSWD = "password"
UHASH = 'fe9dfc91b3a89c563a15c1f9d7a1467c08fcb6621a14cfa791014f45bcfac0e3'
SALT = 'mh3ot3si9anq'
USER_FIELDS = {'age': 24}

_tmpdir = '%s/tmp' % os.path.dirname(__file__)

class TestWaltz(unittest.TestCase):
    
    def setUp(self):
        self.assertTrue(not os.path.exists(_tmpdir))
        os.makedirs(_tmpdir)        
        waltz.setup.init_scaffolding(_tmpdir)
        with open('%s/__init__.py' % _tmpdir, 'w') as f:
            f.write("")

    def test_accounts(self):
        user = Account.register(USERNAME, PASSWD, salt=SALT, **USER_FIELDS)
        self.assertTrue(all(item in user.items() for item in USER_FIELDS.items()),
                        "USER_FIELDS: %s did not persist to user: %s "\
                            % (USER_FIELDS, user))
        self.assertTrue(user.uhash == UHASH,
                        "waltz.Account.register(%s, %s, salt=%s) " \
                            "expected result hash of " \
                            "%s but generated uhash: %s " \
                            % (USERNAME, PASSWD, SALT, UHASH, user.uhash))
        self.assertTrue(user.uhash == UHASH,
                        "waltz.Account.register(%s, %s, salt=%s) " \
                            "expected result  of " \
                            "%s but generated uhash: %s " \
                            % (USERNAME, PASSWD, SALT, UHASH, user.uhash))

    def test_run(self):
        middleware = []
        #waltzapp = __import__() # XXX! '%s/main.py' % _tmpdir
        #self.assertTrue(hasattr(waltzapp, 'env'), "Failed to load waltz app")
        #print waltzapp.env
        #app = TestApp(.wsgifunc(*middleware))
        #r = testApp.get('/')
        #assert_equal(r.status, 200)
        #r.mustcontain('Hello, world!')

    def test_users(self):
        """Test whether waltz.User (of base type Account) interfaces
        with LazyDB correctly and behaves expectedly
        """
        # Setting up waltz web.py env variables for db()
        web.ctx.waltz = storage()
        web.ctx.waltz.db = 'db'

        u1 = User.register(USERNAME, PASSWD, **USER_FIELDS)
        u2 = User.get(USERNAME)
        u3 = User.register(USERNAME[::-1], PASSWD, **USER_FIELDS)

        self.assertTrue(u1['username'] == USERNAME,
                        "<waltz.User.register> Registration " \
                            "returned invalid user dict")
        self.assertTrue(u2 is not None, "<waltz.User.register> " \
                            "Registration failed, no such entry " \
                            "indexed by {'username': '%s'}" % USERNAME)
        self.assertTrue(all(item in u2.items() for item in USER_FIELDS.items()),
                        "<waltz.User.get> Expected stored data did not match " \
                            "actual data indexed by waltz 'user' LazyDB.")
        User.replace(USERNAME, u3)
        self.assertTrue(User.get(USERNAME)['username'] == USERNAME[::-1],
                        "<waltz.User.replace> Failed to replace username")
        u4 = User.get(USERNAME[::-1], safe=True)
        self.assertTrue(not getattr(u4, 'uhash', False),
                        "User.get(%s, safe=True) did not remove uhash field " \
                            "as would be expected" % USERNAME[::-1])
        users = User.getall()
        self.assertTrue(len(users) == 2, "Users db has incorrect # users: " \
                        "%s (%s)" % (len(users), users))
        users2 = User.getall(safe=True)
        self.assertTrue('uhash' not in users2[USERNAME].keys(),
                        "User.getall(safe=True) did not remove uhash field " \
                            "as would be expected")
        self.assertTrue(User.delete(USERNAME) is not None,
                        "<waltz.User.delete> " \
                            "Failed to delete user: %s" % USERNAME)
    def tearDown(self):
        if os.path.isfile('db'): os.remove('db')
        self.assertTrue(os.path.exists(_tmpdir),
                        "Can't find the tmp directory <Dir: %s>" \
                            ", it should exist!" % _tmpdir)
        shutil.rmtree(_tmpdir)
        self.assertTrue(not os.path.exists(_tmpdir),
                        "tmp directory <Dir: %s> should have been cleaned up" \
                            "/ removed however it still exists!" % _tmpdir)
