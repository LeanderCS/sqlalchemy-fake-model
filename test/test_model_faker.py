from datetime import date, datetime
import uuid

import pytest
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    Interval,
    LargeBinary,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID, JSON, JSONB
from sqlalchemy.types import DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_fake_model import ModelFaker
from sqlalchemy_fake_model.Error import InvalidAmountError, UniquenessError
from sqlalchemy_fake_model.Model import ModelFakerConfig

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
    json_list_field = Column(
        Text,
        nullable=False,
        doc='["string", "integer", "float", "date", "datetime"]',
    )
    json_obj_field = Column(
        Text,
        nullable=False,
        doc='{"street": "string", '
        '"location": '
        '{"city": "string", "zip": "integer"}}',
    )


@pytest.fixture(scope="function")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="function")
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

    class MyFlaskModel(db.Model):
        __tablename__ = "myflaskmodel"
        id = db.Column(db.Integer, primary_key=True)
        string_field = db.Column(db.String(80), nullable=False)
        short_string_field = db.Column(db.String(5), nullable=False)
        long_string_field = db.Column(db.String(255), nullable=False)
        nullable_field = db.Column(db.String(80), nullable=True)
        boolean_field = db.Column(db.Boolean, nullable=False)
        default_field = db.Column(
            db.String(80), nullable=False, default="test123"
        )
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
        model_faker = ModelFaker(MyFlaskModel)
        model_faker.create(amount=5)
        fake_entries = db.session.query(MyFlaskModel).all()
        assert len(fake_entries) == 5


def test_tornado_integration() -> None:
    """Test the tornado integration."""
    from tornado.web import Application

    app = Application()
    app.settings["db"] = sessionmaker(
        bind=create_engine("sqlite:///:memory:")
    )()

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


def test_create_fake_data_invalid_amount(fake_data, session) -> None:
    """
    Test if the ModelFaker is able to create fake data and validate each field.
    """
    with pytest.raises(InvalidAmountError):
        fake_data.create(amount="invalid")


def test_nullable_field(fake_data, session) -> None:
    """
    Test if the nullable fields are handled correctly by ModelFaker.
    """
    fake_data.create()

    entry = session.query(MyModel).first()
    assert entry.nullable_field is None


def test_nullable_field_fill(fake_data, session) -> None:
    """
    Test if the nullable fields are handled correctly by ModelFaker.
    """
    ModelFaker(
        MyModel, session, config=ModelFakerConfig(fill_nullable_fields=True)
    ).create()

    entry = session.query(MyModel).first()
    assert entry.nullable_field is not None


def test_default_value(fake_data, session) -> None:
    """
    Test if the default value is correctly set (for price).
    """
    fake_data.create()

    entry = session.query(MyModel).first()
    assert entry.default_field == "test123"


def test_default_value_fill(fake_data, session) -> None:
    """
    Test if the default value is correctly set (for price).
    """
    ModelFaker(
        MyModel, session, config=ModelFakerConfig(fill_default_fields=True)
    ).create()

    entry = session.query(MyModel).first()
    assert entry.default_field != "test123"


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
    assert len(json_data) == 5

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


def test_foreign_key(fake_data, session) -> None:
    """
    Test if the foreign key field is handled correctly.
    """

    class MyModelForeignKey(Base):

        __tablename__ = "mymodel_foreignkey"

        id = Column(Integer, primary_key=True)
        foreign_key = Column(Integer, ForeignKey("mymodel.id"), nullable=False)

    Base.metadata.create_all(session.bind)

    fake_foreign_entries = session.query(MyModel).all()
    assert len(fake_foreign_entries) == 0

    ModelFaker(MyModelForeignKey, session).create()

    fake_entries = session.query(MyModelForeignKey).all()
    assert len(fake_entries) == 1

    fake_foreign_entries = session.query(MyModel).all()
    assert len(fake_foreign_entries) == 1


def test_foreign_key_not_id(fake_data, session) -> None:
    """
    Test if the foreign key field is handled correctly.
    """

    class MyModel2(Base):

        __tablename__ = "mymodel2"

        name = Column(String, primary_key=True)

    class MyModel3(Base):

        __tablename__ = "mymodel3"

        id = Column(Integer, primary_key=True)
        foreign_key = Column(
            String, ForeignKey("mymodel2.name"), nullable=False
        )

    Base.metadata.create_all(session.bind)

    fake_foreign_entries = session.query(MyModel2).all()
    assert len(fake_foreign_entries) == 0

    ModelFaker(MyModel3, session).create()

    fake_entries = session.query(MyModel3).all()
    assert len(fake_entries) == 1

    fake_foreign_entries = session.query(MyModel2).all()
    assert len(fake_foreign_entries) == 1


def test_new_data_types(session) -> None:
    """Test the new data types functionality."""

    class ExtendedModel(Base):
        __tablename__ = "extended_model"

        id = Column(Integer, primary_key=True)
        uuid_field = Column(String, nullable=False)
        decimal_field = Column(DECIMAL(10, 2), nullable=False)
        time_field = Column(Time, nullable=False)
        interval_field = Column(String, nullable=False)  # Interval as string for SQLite
        binary_field = Column(LargeBinary, nullable=False)
        json_field = Column(Text, nullable=False)  # JSON as text for SQLite

    Base.metadata.create_all(session.bind)

    ModelFaker(ExtendedModel, session).create(amount=3)

    entries = session.query(ExtendedModel).all()
    assert len(entries) == 3

    for entry in entries:
        assert entry.uuid_field is not None
        assert entry.decimal_field is not None
        assert entry.time_field is not None
        assert entry.interval_field is not None
        assert entry.binary_field is not None
        assert entry.json_field is not None


def test_smart_field_detection_integration(session) -> None:
    """Test smart field detection integration with ModelFaker."""

    class SmartModel(Base):
        __tablename__ = "smart_model"

        id = Column(Integer, primary_key=True)
        email = Column(String(255), nullable=False)
        first_name = Column(String(100), nullable=False)
        last_name = Column(String(100), nullable=False)
        phone = Column(String(20), nullable=False)
        company = Column(String(200), nullable=False)
        age = Column(Integer, nullable=False)
        price = Column(Float, nullable=False)

    Base.metadata.create_all(session.bind)

    config = ModelFakerConfig(smart_detection=True)
    ModelFaker(SmartModel, session, config=config).create(amount=2)

    entries = session.query(SmartModel).all()
    assert len(entries) == 2

    for entry in entries:
        assert "@" in entry.email
        assert entry.age >= 1 and entry.age <= 100
        assert entry.price >= 0


def test_smart_detection_disabled(session) -> None:
    """Test that smart detection can be disabled."""

    class BasicModel(Base):
        __tablename__ = "basic_model"

        id = Column(Integer, primary_key=True)
        email = Column(String(255), nullable=False)
        age = Column(Integer, nullable=False)

    Base.metadata.create_all(session.bind)

    config = ModelFakerConfig(smart_detection=False)
    faker = ModelFaker(BasicModel, session, config=config)

    # Smart detector should not be created
    assert faker.smart_detector is None

    faker.create(amount=1)
    entries = session.query(BasicModel).all()
    assert len(entries) == 1

    # Email might not contain @ since smart detection is disabled
    entry = entries[0]
    assert isinstance(entry.email, str)
    assert isinstance(entry.age, int)


def test_field_overrides(session) -> None:
    """Test custom field overrides."""

    class OverrideModel(Base):
        __tablename__ = "override_model"

        id = Column(Integer, primary_key=True)
        name = Column(String(100), nullable=False)
        status = Column(String(50), nullable=False)

    Base.metadata.create_all(session.bind)

    def custom_status():
        return "ACTIVE"

    config = ModelFakerConfig(
        field_overrides={
            "status": custom_status
        }
    )

    ModelFaker(OverrideModel, session, config=config).create(amount=3)

    entries = session.query(OverrideModel).all()
    assert len(entries) == 3

    for entry in entries:
        assert entry.status == "ACTIVE"


def test_create_batch_without_commit(session) -> None:
    """Test create_batch without committing."""

    faker = ModelFaker(MyModel, session)
    instances = faker.create_batch(amount=5, commit=False)

    assert len(instances) == 5
    committed_entries = session.query(MyModel).all()
    assert len(committed_entries) == 0


def test_create_batch_with_commit(session) -> None:
    """Test create_batch with committing."""

    faker = ModelFaker(MyModel, session)
    instances = faker.create_batch(amount=3, commit=True)

    assert len(instances) == 3
    committed_entries = session.query(MyModel).all()
    assert len(committed_entries) == 3


def test_create_with_overrides(session) -> None:
    """Test create_with method."""

    faker = ModelFaker(MyModel, session)
    overrides = {
        "string_field": "Custom Value",
        "integer_field": 42,
        "boolean_field": True
    }

    instances = faker.create_with(overrides, amount=2)

    assert len(instances) == 2
    entries = session.query(MyModel).all()
    assert len(entries) == 2

    for entry in entries:
        assert entry.string_field == "Custom Value"
        assert entry.integer_field == 42
        assert entry.boolean_field == True


def test_reset_functionality(session) -> None:
    """Test reset method."""

    faker = ModelFaker(MyModel, session)
    faker.create(amount=5)

    initial_count = session.query(MyModel).count()
    assert initial_count == 5

    deleted_count = faker.reset(confirm=True)
    assert deleted_count == 5

    final_count = session.query(MyModel).count()
    assert final_count == 0


def test_reset_requires_confirmation(session) -> None:
    """Test that reset requires confirmation."""

    faker = ModelFaker(MyModel, session)
    faker.create(amount=3)

    with pytest.raises(ValueError, match="Must set confirm=True"):
        faker.reset()


def test_context_manager(session) -> None:
    """Test context manager functionality."""

    with ModelFaker(MyModel, session) as faker:
        faker.create(amount=2)

    entries = session.query(MyModel).all()
    assert len(entries) == 2


def test_seed_reproducibility(session) -> None:
    """Test that seed produces reproducible results."""

    config1 = ModelFakerConfig(seed=12345)
    config2 = ModelFakerConfig(seed=12345)

    faker1 = ModelFaker(MyModel, session, config=config1)
    faker2 = ModelFaker(MyModel, session, config=config2)

    # Clear any existing data
    session.query(MyModel).delete()
    session.commit()

    faker1.create(amount=1)
    first_entry = session.query(MyModel).first()
    first_values = {
        'string_field': first_entry.string_field,
        'integer_field': first_entry.integer_field,
        'boolean_field': first_entry.boolean_field
    }

    # Clear and create with second faker
    session.query(MyModel).delete()
    session.commit()

    faker2.create(amount=1)
    second_entry = session.query(MyModel).first()
    second_values = {
        'string_field': second_entry.string_field,
        'integer_field': second_entry.integer_field,
        'boolean_field': second_entry.boolean_field
    }

    assert first_values == second_values


def test_bulk_creation(session) -> None:
    """Test bulk creation with large amounts."""

    config = ModelFakerConfig(bulk_size=100)
    faker = ModelFaker(MyModel, session, config=config)

    faker.create(amount=250)  # Should create in 3 batches

    entries = session.query(MyModel).all()
    assert len(entries) == 250


def test_edge_case_zero_amount(session) -> None:
    """Test creating zero records."""
    faker = ModelFaker(MyModel, session)
    faker.create(amount=0)

    entries = session.query(MyModel).all()
    assert len(entries) == 0


def test_edge_case_large_bulk_size(session) -> None:
    """Test with very large bulk size."""
    config = ModelFakerConfig(bulk_size=10000)
    faker = ModelFaker(MyModel, session, config=config)

    faker.create(amount=5)  # Should use single batch

    entries = session.query(MyModel).all()
    assert len(entries) == 5


def test_edge_case_bulk_size_one(session) -> None:
    """Test with bulk size of 1."""
    config = ModelFakerConfig(bulk_size=1)
    faker = ModelFaker(MyModel, session, config=config)

    faker.create(amount=3)  # Should create 3 separate batches

    entries = session.query(MyModel).all()
    assert len(entries) == 3


def test_edge_case_negative_amount(session) -> None:
    """Test that negative amounts raise error."""
    faker = ModelFaker(MyModel, session)

    with pytest.raises(InvalidAmountError):
        faker.create(amount=-1)


def test_edge_case_string_amount(session) -> None:
    """Test that string amounts raise error."""
    faker = ModelFaker(MyModel, session)

    with pytest.raises(InvalidAmountError):
        faker.create(amount="5")


def test_edge_case_float_amount(session) -> None:
    """Test that float amounts raise error."""
    faker = ModelFaker(MyModel, session)

    with pytest.raises(InvalidAmountError):
        faker.create(amount=5.5)


def test_edge_case_none_amount(session) -> None:
    """Test that None amount raises error."""
    faker = ModelFaker(MyModel, session)

    with pytest.raises(InvalidAmountError):
        faker.create(amount=None)


def test_edge_case_empty_overrides(session) -> None:
    """Test create_with with empty overrides."""
    faker = ModelFaker(MyModel, session)
    instances = faker.create_with({}, amount=2)

    assert len(instances) == 2
    entries = session.query(MyModel).all()
    assert len(entries) == 2


def test_edge_case_none_overrides(session) -> None:
    """Test create_with with None values in overrides."""
    faker = ModelFaker(MyModel, session)
    overrides = {
        "nullable_field": None,
        "string_field": "test"
    }

    instances = faker.create_with(overrides, amount=1)

    assert len(instances) == 1
    entry = instances[0]
    assert entry.nullable_field is None
    assert entry.string_field == "test"


def test_edge_case_invalid_field_override(session) -> None:
    """Test field override with non-existent field."""
    faker = ModelFaker(MyModel, session)
    overrides = {
        "non_existent_field": "value",
        "string_field": "test"
    }

    # Should not raise error, just ignore the non-existent field
    instances = faker.create_with(overrides, amount=1)
    assert len(instances) == 1


def test_edge_case_create_batch_zero(session) -> None:
    """Test create_batch with zero amount."""
    faker = ModelFaker(MyModel, session)
    instances = faker.create_batch(amount=0, commit=False)

    assert len(instances) == 0


def test_edge_case_reset_empty_table(session) -> None:
    """Test reset on empty table."""
    faker = ModelFaker(MyModel, session)

    # Table is already empty
    deleted_count = faker.reset(confirm=True)
    assert deleted_count == 0


def test_edge_case_multiple_resets(session) -> None:
    """Test multiple consecutive resets."""
    faker = ModelFaker(MyModel, session)
    faker.create(amount=3)

    # First reset
    deleted_count1 = faker.reset(confirm=True)
    assert deleted_count1 == 3

    # Second reset on empty table
    deleted_count2 = faker.reset(confirm=True)
    assert deleted_count2 == 0


def test_edge_case_context_manager_exception(session) -> None:
    """Test context manager with exception."""

    class FailingModel(Base):
        __tablename__ = "failing_model"
        id = Column(Integer, primary_key=True)
        # This will cause issues with the test setup

    try:
        with ModelFaker(FailingModel, session) as faker:
            # This might fail due to table not existing
            faker.create(amount=1)
    except Exception:
        # Expected to fail, but context manager should handle cleanup
        pass


def test_edge_case_very_long_string_field(session) -> None:
    """Test with very long string length."""

    class LongStringModel(Base):
        __tablename__ = "long_string_model"
        id = Column(Integer, primary_key=True)
        very_long_field = Column(String(10000), nullable=False)

    Base.metadata.create_all(session.bind)

    faker = ModelFaker(LongStringModel, session)
    faker.create(amount=1)

    entries = session.query(LongStringModel).all()
    assert len(entries) == 1
    assert len(entries[0].very_long_field) <= 10000


def test_edge_case_custom_faker_instance(session) -> None:
    """Test with custom Faker instance."""
    from faker import Faker

    custom_faker = Faker('de_DE')
    custom_faker.seed_instance(12345)

    config = ModelFakerConfig(faker_instance=custom_faker)
    faker = ModelFaker(MyModel, session, config=config)

    faker.create(amount=1)
    entries = session.query(MyModel).all()
    assert len(entries) == 1


def test_edge_case_mixed_configurations(session) -> None:
    """Test mixed configuration options."""

    def custom_string():
        return "CUSTOM_VALUE"

    config = ModelFakerConfig(
        locale="fr_FR",
        seed=54321,
        smart_detection=True,
        fill_nullable_fields=True,
        fill_default_fields=True,
        bulk_size=50,
        field_overrides={
            "string_field": custom_string
        }
    )

    faker = ModelFaker(MyModel, session, config=config)
    faker.create(amount=2)

    entries = session.query(MyModel).all()
    assert len(entries) == 2

    for entry in entries:
        assert entry.string_field == "CUSTOM_VALUE"
        assert entry.nullable_field is not None  # Should be filled
        assert entry.default_field != "test123"  # Should be overridden


def test_edge_case_concurrent_access(session) -> None:
    """Test multiple ModelFaker instances on same model."""

    faker1 = ModelFaker(MyModel, session)
    faker2 = ModelFaker(MyModel, session)

    faker1.create(amount=2)
    faker2.create(amount=3)

    entries = session.query(MyModel).all()
    assert len(entries) == 5


def test_edge_case_field_override_callable_error(session) -> None:
    """Test field override with callable that raises exception."""

    def failing_override():
        raise ValueError("Override failed")

    config = ModelFakerConfig(
        field_overrides={
            "string_field": failing_override
        }
    )

    faker = ModelFaker(MyModel, session, config=config)

    with pytest.raises(RuntimeError, match="Failed to commit"):
        faker.create(amount=1)


def test_edge_case_extremely_large_integer_range(session) -> None:
    """Test with extremely large integer ranges."""

    class LargeIntModel(Base):
        __tablename__ = "large_int_model"
        id = Column(Integer, primary_key=True)
        large_int = Column(Integer, nullable=False, info={"min": 1000000, "max": 9999999})

    Base.metadata.create_all(session.bind)

    faker = ModelFaker(LargeIntModel, session)
    faker.create(amount=1)

    entries = session.query(LargeIntModel).all()
    assert len(entries) == 1
    assert 1000000 <= entries[0].large_int <= 9999999
