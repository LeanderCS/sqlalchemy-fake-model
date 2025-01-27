from datetime import date, datetime

import pytest
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_fake_model import ModelFaker

"""
Test the ModelFaker class
"""

Base = declarative_base()


class MyModel(Base):
    """
    A simple SQLAlchemy model for testing the ModelFaker class
    """

    __tablename__ = "mymodel"

    id = Column(Integer, primary_key=True)
    string_field = Column(String(80), nullable=False)
    short_string_field = Column(String(5), nullable=False)
    long_string_field = Column(String(255), nullable=False)
    nullable_field = Column(String(80), nullable=True)
    boolean_field = Column(Boolean, nullable=False)
    default_field = Column(String(80), nullable=False, default="test123")
    integer_field = Column(Integer, nullable=False)
    max_min_integer_field = Column(
        Integer, nullable=False, info={"min": 100, "max": 101}
    )
    float_field = Column(Float((5, 2)), nullable=False)
    date_field = Column(Date, nullable=False)
    datetime_field = Column(DateTime, nullable=False)
    json_list_field = Column(Text, nullable=False, doc='["string", "integer"]')
    json_obj_field = Column(
        Text,
        nullable=False,
        doc='{"street": "string", '
        '"location": '
        '{"city": "string", "zip": "integer"}}',
    )


@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="module")
def session(engine):
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def fake_data(session) -> ModelFaker:
    """
    Fixture to create fake data for the MyModel model.
    """
    model_faker = ModelFaker(MyModel, session)

    return model_faker


def test_flask_integration() -> None:
    """Test the Flask integration."""
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db = SQLAlchemy(app)

    class MyModel2(db.Model):
        __tablename__ = "mymodel2"
        id = db.Column(db.Integer, primary_key=True)
        string_field = db.Column(db.String(80), nullable=False)
        short_string_field = db.Column(db.String(5), nullable=False)
        long_string_field = db.Column(db.String(255), nullable=False)
        nullable_field = db.Column(db.String(80), nullable=True)
        boolean_field = db.Column(db.Boolean, nullable=False)
        default_field = db.Column(
            db.String(80), nullable=False, default="test123")
        integer_field = db.Column(db.Integer, nullable=False)
        max_min_integer_field = db.Column(
            db.Integer, nullable=False, info={"min": 100, "max": 101}
        )
        float_field = db.Column(db.Float, nullable=False)
        date_field = db.Column(db.Date, nullable=False)
        datetime_field = db.Column(db.DateTime, nullable=False)
        json_list_field = db.Column(
            db.Text, nullable=False, doc='["string", "integer"]'
        )
        json_obj_field = db.Column(
            db.Text,
            nullable=False,
            doc='{"street": "string", "location": '
            '{"city": "string", "zip": "integer"}}',
        )

    with app.app_context():
        db.create_all()
        model_faker = ModelFaker(MyModel2)
        model_faker.create(amount=5)
        fake_entries = db.session.query(MyModel2).all()
        assert len(fake_entries) == 5


def test_tornado_integration() -> None:
    """Test the tornado integration."""
    from tornado.web import Application

    app = Application()
    app.settings["db"] = sessionmaker(
        bind=create_engine("sqlite:///:memory:"))()

    Base.metadata.create_all(app.settings["db"].bind)
    model_faker = ModelFaker(MyModel, app.settings["db"])
    model_faker.create(amount=5)
    fake_entries = app.settings["db"].query(MyModel).all()
    assert len(fake_entries) == 5


def test_django_integration() -> None:
    """Test the Django integration."""
    import django
    from django.conf import settings
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    settings.configure(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        }
    )
    django.setup()

    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()

    Base.metadata.create_all(engine)
    model_faker = ModelFaker(MyModel, session)
    model_faker.create(amount=5)
    fake_entries = session.query(MyModel).all()
    assert len(fake_entries) == 5


def test_create_fake_data(fake_data, session) -> None:
    """
    Test if the ModelFaker is able to create fake data and validate each field.
    """
    fake_data.create(amount=5)

    fake_entries = session.query(MyModel).all()
    assert len(fake_entries) == 5


def test_nullable_field(fake_data, session) -> None:
    """
    Test if the nullable fields are handled correctly by ModelFaker.
    """

    fake_data.create()

    entry = session.query(MyModel).first()
    assert entry.nullable_field is None


def test_default_value(fake_data, session) -> None:
    """
    Test if the default value is correctly set (for price).
    """

    fake_data.create()

    entry = session.query(MyModel).first()
    assert entry.default_field == "test123"


def test_string_field(fake_data, session) -> None:
    """
    Test if the string field is handled correctly.
    """

    fake_data.create()

    entry = session.query(MyModel).first()
    assert isinstance(entry.string_field, str)


def test_integer_field(fake_data, session) -> None:
    """
    Test if the integer field is handled correctly.
    """

    fake_data.create()

    entry = session.query(MyModel).first()
    assert isinstance(entry.integer_field, int)


def test_max_min_integer_field(fake_data, session) -> None:
    """
    Test if the integer field is handled correctly.
    """

    fake_data.create()

    entry = session.query(MyModel).first()
    assert isinstance(entry.max_min_integer_field, int)
    assert entry.max_min_integer_field >= 100
    assert entry.max_min_integer_field <= 101


def test_float_field(fake_data, session) -> None:
    """
    Test if the integer field is handled correctly.
    """

    fake_data.create()

    entry = session.query(MyModel).first()
    assert isinstance(entry.float_field, float)

    precision = len(str(entry.float_field).replace(".", "").replace("-", ""))
    assert precision <= 5

    scale = (
        len(str(entry.float_field).split(".")[1])
        if "." in str(entry.float_field)
        else 0
    )
    assert scale <= 2


def test_bool_field(fake_data, session) -> None:
    """
    Test if the bool field is handled correctly.
    """

    fake_data.create()

    entry = session.query(MyModel).first()
    assert isinstance(entry.boolean_field, bool)


def test_date_field(fake_data, session) -> None:
    """
    Test if the date field is handled correctly.
    """

    fake_data.create()

    entry = session.query(MyModel).first()
    assert isinstance(entry.date_field, date)


def test_datetime_field(fake_data, session) -> None:
    """
    Test if the datetime field is handled correctly.
    """

    fake_data.create()

    entry = session.query(MyModel).first()
    assert isinstance(entry.datetime_field, datetime)


def test_json_list_field(fake_data, session) -> None:
    """
    Test if the json field is handled correctly.
    """

    fake_data.create()

    entry = session.query(MyModel).first()

    assert entry.json_list_field is not None
    assert isinstance(entry.json_list_field, str)

    json_data = eval(entry.json_list_field)
    assert isinstance(json_data, list)
    assert len(json_data) == 2

    assert isinstance(json_data[0], str)
    assert isinstance(json_data[1], int)


def test_json_obj_field(fake_data, session) -> None:
    """
    Test if the json field is handled correctly.
    """

    fake_data.create()

    entry = session.query(MyModel).first()
    assert isinstance(entry.json_obj_field, str)

    json_data = eval(entry.json_obj_field)
    assert isinstance(json_data, dict)

    assert isinstance(json_data["street"], str)
    assert isinstance(json_data["location"], dict)
    assert isinstance(json_data["location"]["city"], str)
    assert isinstance(json_data["location"]["zip"], int)
