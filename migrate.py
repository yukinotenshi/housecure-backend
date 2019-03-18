from playhouse.migrate import *


db = SqliteDatabase('data.db')
migrator = SqliteMigrator(db)

room_x = IntegerField(default=3)
room_y = IntegerField(default=3)

migrate(
    migrator.add_column('device', 'room_x', room_x),
    migrator.add_column('device', 'room_y', room_y)
)
