from peewee import *
from core.config_manager import create_database_connection

# Создаем подключение к базе данных
database = create_database_connection('school_world')


class BaseModel(Model):
    class Meta:
        database = database


class Teacher(BaseModel):
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    subject = CharField(max_length=50)

    class Meta:
        table_name = 'teachers'


class Class(BaseModel):
    name = CharField(max_length=10, unique=True)
    classroom = CharField(max_length=10)

    class Meta:
        table_name = 'classes'


class Student(BaseModel):
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    birth_date = DateField()
    class_id = ForeignKeyField(Class, backref='students')

    class Meta:
        table_name = 'students'


class Subject(BaseModel):
    name = CharField(max_length=50)
    teacher_id = ForeignKeyField(Teacher, backref='subjects')

    class Meta:
        table_name = 'subjects'


class Grade(BaseModel):
    student_id = ForeignKeyField(Student, backref='grades')
    subject_id = ForeignKeyField(Subject, backref='grades')
    grade = IntegerField()
    date = DateField()

    class Meta:
        table_name = 'grades'


# Список всех моделей для этой БД
MODELS = [Teacher, Class, Student, Subject, Grade]


def get_models():
    return MODELS


def get_database():
    return database
