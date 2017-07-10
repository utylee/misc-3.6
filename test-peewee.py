from peewee import *

db = SqliteDatabase('pw.db')

class Akiba(Model):
    code = CharField()

    class Meta:
        database = db


db.connect()
#db.create_tables([Akiba])
