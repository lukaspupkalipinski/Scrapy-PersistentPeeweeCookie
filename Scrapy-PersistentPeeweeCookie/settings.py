#!/usr/bin/env python
"""This setting file is an example for the usage of the Scrapy-PersistentPeeweeCookie.

This setting file is an example for the usage of the Scrapy-PersistentPeeweeCookie.
It contains the basic needed configuration.
Most important is the DOWNLOADER_MIDDLEWARES entry and the Database creation PersistentPeeweeCookie.

"""

from peewee import *

__author__ = "Lukas Pupka-Lipinski"
__copyright__ = "Copyright 2018, PersistentPeeweeCookie"
__credits__ = [""]
__license__ = "GPL"
__version__ = "1.0.5"
__maintainer__ = "Lukas Pupka-Lipinski"
__email__ = "support@lpl-mind.de"
__status__ = "Dev"

DOWNLOADER_MIDDLEWARES = {

    'Fbworker.middleware.CookiesMiddleware.CookiesMiddleware':701
}

COOKIES_DEBUG=True
COOKIES_ENABLED=True

MYSQL_SERVER = '192.168.178.47'
MYSQL_USERNAME = 'user'
MYSQL_PASSWORD = 'password'
MYSQL_DATABASE = 'databasename'


PersistendPeeweeCookie =  MySQLDatabase(user=MYSQL_SERVER,password=MYSQL_USERNAME,host=MYSQL_PASSWORD,database=MYSQL_DATABASE)