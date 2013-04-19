# Waltz

![Build Status](https://travis-ci.org/mekarpeles/waltz.png)

Waltz is a web.py based web framework for rapidly designing
web apps in 3/4 time. Waltz comes pre-configured, ready to run, and
includes features like out-of-the-box support for analytics
tracking. Waltz and never miss a beat.

## Installation

You may wish to install with the --upgrade flag since updates pushed are frequently.

    # Installing the latest stable build from pypi
    $ pip install waltz
    
    # Upgrading your waltz package using pypi
    $ pip install waltz --upgrade
    
    # Build latest from github
    $ git clone http://github.com/mekarpeles/waltz
    $ cd waltz
    $ pip install . --upgrade    

## Running

    $ mkidir project
    $ cd project
    $ waltz init
    $ python main.py <port>

## Docs

The documentation is currently out of date and will be synced up for the 0.1.70 release: https://github.com/mekarpeles/waltz/wiki

## Tests

You can run the waltz test by invoking 'nosetests' from the top level waltz directory.
