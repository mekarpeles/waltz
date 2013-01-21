#!/usr/bin/env python

"""waltz: make web apps in 3/4 time (http://github.com/mekarpeles/waltz)"""

__version__ = "0.1.6"
__author__ = [
    "Mek <michael.karpeles@gmail.com>"
]
__license__ = "public domain"
__contributors__ = "see AUTHORS"

import web
import os
from lazydb import Db

session = lambda: getattr(web.ctx, 'session', None)
render = lambda: getattr(web.ctx, 'render', None)
db = Db('%s/db' % os.getcwd())

from security import User
from decorations import *
from utils import *
from treasury import *
from setup import *
