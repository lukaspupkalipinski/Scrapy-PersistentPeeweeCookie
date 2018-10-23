from peewee import *
from scrapy.utils.project import get_project_settings


settings = get_project_settings()
db = settings['PersistendPeeweeCookie-Database']

db.connect()

class BaseModel(Model):
    class Meta:
        database = db





