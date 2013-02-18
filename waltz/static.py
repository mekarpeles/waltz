#-*- coding: utf-8 -*-
"""
    static
    ~~~~~~
    Static html resources to render during scaffolding
"""

index = """$def with()

<h1>Darling, we're ready to waltz!</h1>
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
    <link rel="stylesheet" href="">
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
