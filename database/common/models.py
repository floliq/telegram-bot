import os
from datetime import datetime
import peewee as pw
from peewee import SqliteDatabase

db: SqliteDatabase = pw.SqliteDatabase("database.db")
db.pragma("foreign_keys", 1, permanent=True)


class ModelBase(pw.Model):
    class Meta:
        database = db


class User(ModelBase):
    chat_id = pw.BigIntegerField(unique=True)
    action = pw.IntegerField(null=True)
    order = pw.CharField(max_length=255, null=True)
    destination_id = pw.CharField(max_length=255, null=True)
    date_in = pw.DateField(null=True)
    date_out = pw.DateField(null=True)
    person_count = pw.IntegerField(default=1)
    min_price = pw.IntegerField(null=True)
    max_price = pw.IntegerField(null=True)


class History(ModelBase):
    user_id = pw.ForeignKeyField(User)
    date_time = pw.DateTimeField(default=datetime.now())
    event = pw.CharField(max_length=255)
    search_result = pw.TextField()


db.create_tables([User, History])
