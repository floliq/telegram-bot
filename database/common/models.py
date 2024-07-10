import os
from datetime import datetime
import peewee as pw
from peewee import SqliteDatabase

db: SqliteDatabase = pw.SqliteDatabase("database.db")
db.pragma('foreign_keys', 1, permanent=True)


class ModelBase(pw.Model):
    class Meta:
        database = db


class User(ModelBase):
    chat_id = pw.BigIntegerField(unique=True)
    action = pw.IntegerField(default='0')
    # currency = pw.CharField(max_length=5)
    # order = pw.CharField(max_length=255)
    destination_id = pw.CharField(max_length=255, default='')
    # destination_name = pw.CharField(max_length=255)
    # date_from = pw.CharField(max_length=255)
    # date_to = pw.CharField(max_length=255)


class History(ModelBase):
    user = pw.ForeignKeyField(User)
    date_time = pw.DateTimeField(default=datetime.now())
    event = pw.CharField(max_length=255)
    search_result = pw.TextField()


db.create_tables([User, History])
