"""
   modules
   ~~~~~~~
   Modules/plugins + extras for the waltz framework
"""

from waltz import web, db
from datetime import datetime     
from lazydb import Db

class Analytics:
    def GET(self):
        web.header('Content-Type', 'application/json')
        return db().get('analytics')

def rss(items_func, template=None, **kwargs):
    rss = RSS(template=template, **kwargs)

    class RSSfeed:
        def GET(self):
            web.header('Content-Type', 'application/xml')
            return rss.feed(items_func())
    return RSSfeed

class RSS:

    _template = """$def with (title="", link="", description="", \
 language="en-us", date="", generator="", \
 editor="", webmaster="", items=[])

<!--?xml version="1.0"?-->
<rss version="2.0">
   <channel>
      <title>$title</title>
      <link>$link</link>
      <description>$description</description>
      <language>$language</language>
      <pubdate>$date</pubdate>

      <lastbuilddate>$date</lastbuilddate>
      <generator>$generator</generator>
      <managingeditor>$editor</managingeditor>
      <webmaster>$webmaster</webmaster>

      $for item in items:
        <item>
           <title>$(item['title'] if 'title' in item else '')</title>
           <link>$(item['link'] if  'link' in item else '')</link>
           <description><!--[CDATA[$(item['description'][:100] if 'description' in item else '')..]]--></description>
           <pubdate>$(item['date'] if 'date' in item else '')</pubdate>
           <guid>$(item['guid'] if 'guild' in item else '')</guid>
        </item>
    </channel>
</rss>
"""
    def __init__(self, template=None, **kwargs):
        template = template or self._template
        self.kwargs = kwargs
        if template == self._template:
            for (k, v) in [('title', ''),
                           ('description', ''),
                           ('language', 'en-us'),
                           ('date', datetime.now().ctime()),
                           ('generator', ''),
                           ('editor', 'waltz'),
                           ('webmaster', '')]:
                kwargs.setdefault(k, v)
        self.template = web.template.Template(template)

    def feed(self, items):
        """Example items list for waltz RSS template:

        [{'title': '',
          'link': '',
          'body': '',
          'description': '',
          'date': '',
          'guid': ''
          }, ...
        ]

        :param items: a function which generates item dicts of the
                      above format
        """
        kwargs = {'items': items}
        kwargs.update(self.kwargs)     
        return self.template(**kwargs)
