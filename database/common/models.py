from datetime import datetime
import peewee as pw

db = pw.SqliteDatabase("database.db")


class ModelBase(pw.Model):
    created_at = pw.DateField(default=datetime.now())

    class Meta:
        database = db


class History(ModelBase):
    number = pw.TextField()
    message = pw.TextField()
