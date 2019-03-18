from datetime import datetime
import peewee as pw
from playhouse.shortcuts import model_to_dict


db = pw.SqliteDatabase('data.db')


class BaseModel(pw.Model):
    def to_dict(self):
        return model_to_dict(self)

    class Meta:
        database = db


class User(BaseModel):
    user_key = pw.CharField()
    fcm_key = pw.CharField()


class Device(BaseModel):
    user = pw.ForeignKeyField(User, backref='devices')
    room = pw.CharField()
    device_id = pw.CharField()

    def to_dict(self):
        return model_to_dict(self)


class Log(BaseModel):
    user = pw.ForeignKeyField(User, backref='logs')
    device = pw.ForeignKeyField(Device, backref='logs')
    created_at = pw.DateTimeField(default=datetime.now)
