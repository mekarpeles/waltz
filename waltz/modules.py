"""
   moddules
   ~~~~~~~~
   Modules/plugins + extras for the waltz framework
"""

from waltz import web, db
from datetime import datetime     
from lazydb import Db

class Analytics:
    def GET(self):
        web.header('Content-Type', 'application/json')
        return db().get('analytics')
