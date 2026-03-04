from peewee import *

from core.config_manager import create_database_connection

# Создаем подключение к базе данных
database = create_database_connection('games_easy')


class BaseModel(Model):
    class Meta:
        database = database


class Game(BaseModel):
    title = CharField(max_length=100)
    genre = CharField(max_length=50)
    platform = CharField(max_length=50)
    release_year = IntegerField()
    rating = FloatField()
    developer = CharField(max_length=100)
    price = FloatField()

    class Meta:
        table_name = 'games'


class Review(BaseModel):
    game = ForeignKeyField(Game, column_name='game_id')
    author = CharField(max_length=100)
    rating = FloatField(default=1.0)
    text = CharField(max_length=256)

    class Meta:
        table_name = 'reviews'


# Список всех моделей для этой БД
MODELS = [Game, Review]


def get_models():
    return MODELS


def get_database():
    return database
