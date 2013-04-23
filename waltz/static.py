#-*- coding: utf-8 -*-
"""
    static
    ~~~~~~
    Static html resources to render during scaffolding
"""

index = """$def with()

$# Does this specific template (index.html) require its own css or js dependencies?
$# Uncomment and or modify the following two lines by removing the # symbol

$#css = /static/css/style.css
$#js = /static/js/main.js

<h1>Darling, we're ready to waltz!</h1>
"""

style= """
"""

base = """$def with (content)

<!DOCTYPE html>
<!--[if lt IE 7]> <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]> <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]> <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js"> <!--<![endif]-->
  <head>
    <title></title>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta name="viewport" content="width=device-width">
    <meta name="description" content="">
    <link rel="stylesheet" href="/static/css/style.css">
    $# Dynamically link js files related to $content
    $for src in content.get('js', "").split(" "):
      $if src:
        <script type="text/javascript" src="$src"></script>
    $# Dynamically link css files related to $content
    $for href in content.get('css', "").split(" "):
      $if href:
        <link rel="stylesheet" href="$href" />
  </head>
  <body>
    <!--[if lt IE 7]>                         
        <p class="chromeframe">You are using an <strong>outdated</strong> browser. Please 
	  <a href="http://browsehappy.com/">upgrade your browser</a> or <a href="http://www.google.com/chromeframe/?redirect=true">
	    activate Google Chrome Frame</a> to improve your experience.</a>
        <![endif]-->

    <header>
    </header>

    <div id="content">
      $:content
    </div>

    <script> $# Google Analytics ====================================
      var _gaq=[['_setAccount','XX-XXXXXXXX-X'],['_trackPageview']];
      (function(d,t){var g=d.createElement(t),s=d.getElementsByTagName(t)[0];
      g.src=('https:'==location.protocol?'//ssl':'//www')+'.google-analytics.com/ga.js';
      s.parentNode.insertBefore(g,s)}(document,'script'));
    </script>
  </body>
</html>
"""

mainpy = """#!/usr/bin/python
#-*- coding: utf-8 -*-

\"\"\"
    main.py
    ~~~~~~~

    Main waltz application.

    :copyright: (c) __ by __.
    :license: __ , see LICENSE for more details.
\"\"\"

import waltz

urls = ('/analytics/?', 'waltz.modules.Analytics',
        '/?', 'routes.home.Index')

sessions = {}
env = {}
app = waltz.setup.dancefloor(urls, globals(), sessions=sessions, env=env)

if __name__ == "__main__":
    app.run()
"""

homepy = """#-*- coding: utf-8 -*-

\"\"\"
    routes.home
    ~~~~~~~~~~~

    Routes related to the homepage.

    :copyright: (c) __ by __.
    :license: __ , see LICENSE for more details.
\"\"\"

import waltz
from waltz import track, render

class Index:
    @track
    def GET(self):
        return render().index()
"""
