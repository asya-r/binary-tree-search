from peewee import *
import os
import hashlib
from datetime import datetime
import secrets
import time


COMMON_NOT_SECRET = b"gviyvivwev"
DEPTH = 5  # ~ 115 is maximum for now (2048 is max url length)

pg_db = PostgresqlDatabase(database=os.environ.get('POSTGRES_DB'), user=os.environ.get('POSTGRES_USER'),
                           password=os.environ.get('POSTGRES_PASSWORD'), host='db')


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
    timestamp = TimestampField()
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
    token.timestamp = datetime.timestamp(datetime.now())
    token.save()


def initialize_db():
    try:
        with pg_db:
            pg_db.create_tables([Token])
            # pg_db.execute_sql(open("init.sql", "r").read())
    except:
        time.sleep(3)
        initialize_db()

