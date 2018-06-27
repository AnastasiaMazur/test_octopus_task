import peewee
import peewee_async
from encryption_decryption import generate_keys

database = peewee_async.MySQLDatabase('octopus', user='octopus', password='octopus', host='db', port=3306)

PRIVATE_KEY, PUBLIC_KEY = generate_keys()


class WordsModel(peewee.Model):
    text_with_salt = peewee.FixedCharField(primary_key=True, max_length=255)
    enc_text = peewee.TextField()
    freq = peewee.IntegerField()

    class Meta:
        database = database
        indexes = (
            (('text_with_salt',), True),
        )


class UrlsModel(peewee.Model):
    url_with_salt = peewee.FixedCharField(unique=True, max_length=255)
    url = peewee.FixedCharField(unique=True, max_length=255)
    sentiment_analysis = peewee.FixedCharField(max_length=10)

    class Meta:
        database = database
        indexes = (
            (('url_with_salt', 'url'), True),
        )


WordsModel.create_table(True)
UrlsModel.create_table(True)

objects = peewee_async.Manager(database)
database.set_allow_sync(False)
