from peewee import *

from core.config_manager import create_database_connection

# Создаем подключение к базе данных
database = create_database_connection('air_travel')


class BaseModel(Model):
    class Meta:
        database = database


class Airline(BaseModel):
    iata_code = CharField(max_length=2, unique=True)
    icao_code = CharField(max_length=3, unique=True)
    name = CharField(max_length=100)
    country = CharField(max_length=50, null=True)
    is_active = BooleanField(default=True)

    class Meta:
        table_name = 'airlines'


class Airport(BaseModel):
    iata_code = CharField(max_length=3, unique=True)
    icao_code = CharField(max_length=4, unique=True)
    name = CharField(max_length=150)
    city = CharField(max_length=50)
    country = CharField(max_length=50)
    timezone = CharField(max_length=50, null=True)
    latitude = DecimalField(max_digits=10, decimal_places=8, null=True)
    longitude = DecimalField(max_digits=11, decimal_places=8, null=True)

    class Meta:
        table_name = 'airports'


class Aircraft(BaseModel):
    registration_number = CharField(max_length=10, unique=True)
    model = CharField(max_length=50)
    manufacturer = CharField(max_length=50, null=True)
    capacity_economy = IntegerField(null=True)
    capacity_business = IntegerField(null=True)
    airline = ForeignKeyField(Airline, backref='aircrafts', null=True)
    year_of_production = IntegerField(null=True)  # Используем IntegerField для года

    class Meta:
        table_name = 'aircrafts'


class Flight(BaseModel):
    flight_number = CharField(max_length=10)
    airline = ForeignKeyField(Airline, backref='flights')
    departure_airport = ForeignKeyField(Airport, backref='departure_flights')
    arrival_airport = ForeignKeyField(Airport, backref='arrival_flights')
    departure_time = DateTimeField()
    arrival_time = DateTimeField()
    duration_minutes = IntegerField(null=True)
    aircraft = ForeignKeyField(Aircraft, backref='flights', null=True)
    base_price_economy = DecimalField(max_digits=10, decimal_places=2, null=True)
    base_price_business = DecimalField(max_digits=10, decimal_places=2, null=True)
    status = CharField(max_length=20, default='scheduled',
                       choices=[
                           ('scheduled', 'Запланирован'),
                           ('boarding', 'Посадка'),
                           ('departed', 'Вылетел'),
                           ('arrived', 'Прибыл'),
                           ('delayed', 'Задержан'),
                           ('cancelled', 'Отменен')
                       ])

    class Meta:
        table_name = 'flights'
        indexes = (
            (('departure_time', 'status'), False),
        )


class Passenger(BaseModel):
    ticket_number = CharField(max_length=20, unique=True)
    flight = ForeignKeyField(Flight, backref='passengers')
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    passport_number = CharField(max_length=20)
    nationality = CharField(max_length=50, null=True)
    date_of_birth = DateField(null=True)
    seat_number = CharField(max_length=5, null=True)
    class_type = CharField(max_length=20, choices=[('economy', 'Эконом'), ('business', 'Бизнес')])
    booking_reference = CharField(max_length=10, null=True)
    checked_in = BooleanField(default=False)
    boarding_time = DateTimeField(null=True)

    class Meta:
        table_name = 'passengers'
        indexes = (
            (('passport_number',), False),
            (('flight', 'seat_number'), True),  # Уникальный индекс: место в рейсе
        )


# Список всех моделей для этой БД
MODELS = [Airline, Airport, Aircraft, Flight, Passenger]


def get_models():
    return MODELS


def get_database():
    return database
