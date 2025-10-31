from peewee import *
from config import create_database_connection

# Создаем подключение к базе данных
database = create_database_connection('games_shop')

class BaseModel(Model):
    class Meta:
        database = database

class Game(BaseModel):
    title = CharField(max_length=100)
    genre = CharField(max_length=50)
    platform = CharField(max_length=50)
    release_year = IntegerField()
    price = DecimalField(max_digits=10, decimal_places=2)
    developer = CharField(max_length=100)
    publisher = CharField(max_length=100)
    in_stock = IntegerField(default=0)
    description = TextField(null=True)

    class Meta:
        table_name = 'games'

class Customer(BaseModel):
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    email = CharField(max_length=100, unique=True)
    phone = CharField(max_length=20, null=True)
    registration_date = DateField()
    city = CharField(max_length=50, null=True)

    class Meta:
        table_name = 'customers'

class Order(BaseModel):
    customer = ForeignKeyField(Customer, backref='orders')
    order_date = DateField()
    total_amount = DecimalField(max_digits=10, decimal_places=2)
    status = CharField(max_length=20, default='pending')  # pending, completed, cancelled
    shipping_address = TextField()

    class Meta:
        table_name = 'orders'

class OrderItem(BaseModel):
    order = ForeignKeyField(Order, backref='items')
    game = ForeignKeyField(Game, backref='order_items')
    quantity = IntegerField(default=1)
    unit_price = DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        table_name = 'order_items'

# Список всех моделей для этой БД
MODELS = [Game, Customer, Order, OrderItem]

def get_models():
    return MODELS

def get_database():
    return database