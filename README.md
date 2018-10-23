# Scrapy-PersistentPeeweeCookie

This Project allows to to save your scrapy cookies to an Database.
This is based on Peewee, so that any Database could be used.

Visit LPL-mind.de for addtional informations.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.
### Prerequisites

What things you need to install the software and how to install them

```
pip install peewee
pip install scrapy
```

### Installing

Download Files and edit the Settings.py

Change your credationals
```
MYSQL_SERVER = '192.168.178.47'
MYSQL_USERNAME = 'user'
MYSQL_PASSWORD = 'password'
MYSQL_DATABASE = 'databasename'
```

Or change the Database setting to setup andifferent Database

```
PersistendPeeweeCookie =  MySQLDatabase(user=MYSQL_SERVER,password=MYSQL_USERNAME,host=MYSQL_PASSWORD,database=MYSQL_DATABASE)
```

### Versioning

We use SemVer for versioning. For the versions available, see the tags on this repository.
### Authors

    Lukas Pupka-Lipinski


