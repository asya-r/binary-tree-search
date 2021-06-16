from peewee import *
import os
import hashlib
from datetime import datetime
import secrets
import config


COMMON_NOT_SECRET = b"gviyvivwev"
DEPTH = 50  # 62 is maximum for now (2048 is max url length)


# pg_db = PostgresqlDatabase(database=os.environ['POSTGRES_DB'], user=os.environ['POSTGRES_USER'],
#                            password=os.environ['POSTGRES_PASSWORD'], host='localhost')

pg_db = PostgresqlDatabase(database="dbase", user="dbuser",
                           password="sbhBSHbj2d321", host='db')
# pg_db = PostgresqlDatabase(database="dbase", user="dbuser",
#                            password="sbhBSHbj2d321", host='0.0.0.0')


def create_tables():
    with pg_db:
        pg_db.create_tables([Token])
    print([x for x in Token.select()])


class BaseModel(Model):
    class Meta:
        database = pg_db


class Token(BaseModel):
    user_cookie = CharField(unique=True)
    secret = BlobField()
    timestamp = TimestampField(default=datetime.timestamp(datetime.now()))
    flag_path = CharField()


def generate_flag_path(secret: bytes):
    hsh = hashlib.sha256(secret + COMMON_NOT_SECRET).digest()
    path = ''.join([bin(byte)[2:].zfill(8) for byte in hsh])[:DEPTH]
    return path


def create_new_token(cookie: str):
    now = datetime.now()
    secret = secrets.token_bytes(16)
    token = Token()
    token.user_cookie = cookie
    token.secret = secret
    token.flag_path = generate_flag_path(secret)
    token.save()


def initialize_db():
    with pg_db:
        pg_db.create_tables([Token])
        # pg_db.execute_sql(open("init.sql", "r").read())

