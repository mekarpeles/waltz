import unittest
import os
import waltz
from waltz import User, web, storage

class TestWaltz(unittest.TestCase):           

    def test_users(self):
        """Test whether waltz.User (of base type Account) interfaces
        with LazyDB correctly and behaves expectedly
        """
        # Setting up waltz web.py env variables for db()
        web.ctx.waltz = storage()
        web.ctx.waltz.db = 'db'
        extras = {"skill": 9001, "id": 1337}
        username = 'dancer'
        u1 = User.register(username, "*****", **extras)
        u2 = User.get(username)
        self.assertTrue(u1['username'] == username,
                        "<waltz.User.register> Registration " \
                            "returned invalid user dict")
        self.assertTrue(u2 is not None, "<waltz.User.register> " \
                            "Registration failed, no such entry " \
                            "indexed by {'username': '%s'}" % username)
        self.assertTrue(u2['skill'] == 9001, "<waltz.User.get> " \
                            "Expected stored data did not match " \
                            "actual data indexed by waltz 'user' LazyDB.")
        self.assertTrue(User.delete(username) is not None,
                        "<waltz.User.delete> " \
                            "Failed to delete user: %s" % username)
    def tearDown(self):
        if os.path.isfile('db'): os.remove('db')
