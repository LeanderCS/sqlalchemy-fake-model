sqlalchemy-fake-model
=====================

.. image:: https://img.shields.io/pypi/v/sqlalchemy-fake-model?style=flat-square&label=version
    :target: https://pypi.org/project/sqlalchemy-fake-model/
    :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/sqlalchemy-fake-model
    :target: https://pypi.org/project/sqlalchemy-fake-model/
    :alt: Python Versions

.. image:: https://img.shields.io/github/license/LeanderCS/sqlalchemy-fake-model
    :target: https://github.com/LeanderCS/sqlalchemy-fake-model/blob/main/LICENSE
    :alt: License

.. image:: https://img.shields.io/github/actions/workflow/status/LeanderCS/sqlalchemy-fake-model/test.yaml?branch=main&style=flat-square&label=tests
    :target: https://github.com/LeanderCS/sqlalchemy-fake-model/actions
    :alt: Tests

.. image:: https://img.shields.io/coveralls/LeanderCS/sqlalchemy-fake-model/main.svg?style=flat-square&label=coverage
    :target: https://coveralls.io/r/LeanderCS/sqlalchemy-fake-model
    :alt: Coverage

.. image:: https://static.pepy.tech/badge/sqlalchemy-fake-model/month
    :target: https://pypi.org/project/sqlalchemy-fake-model/
    :alt: Monthly Downloads

.. image:: https://static.pepy.tech/badge/sqlalchemy-fake-model
    :target: https://pypi.org/project/sqlalchemy-fake-model/
    :alt: Total Downloads

Description
-----------

``ModelFaker`` is a powerful utility that generates realistic fake data for SQLAlchemy models.
It leverages the Faker library to create structured, random data that's perfect for
development, testing, and database seeding.

**Key Features:**

- Support for all common SQLAlchemy data types
- Automatic relationship handling (OneToOne, OneToMany, ManyToMany)
- Custom data format generation with JSON support
- Framework integration (Flask, Django, Tornado)
- Configurable min/max values and constraints
- Nullable field support with intelligent defaults

Thank you for using ``sqlalchemy-fake-model``!
==============================================

If you have any questions or suggestions, please feel free to open an issue on GitHub `here <https://github.com/LeanderCS/sqlalchemy-fake-model>`__.

If you don't want to miss any updates, please star the repository.
This will help me to understand how many people are interested in this project.

Installation
============

.. code-block:: bash

    pip install sqlalchemy-fake-model

Quickstart
==========

To use the ``ModelFaker`` module, you need to create a new instance of the ``ModelFaker`` class and pass the SQLAlchemy model you want to generate fake data for.
Now you just need to provide a ``session`` to create the data in.
For that you can either simply pass the session or if you use one of the `Supported Frameworks`_,
you can leave the session empty and the module will try to get the session from the framework.

Usage
-----

**Basic Usage:**

.. code-block:: python

    from sqlalchemy_fake_model import ModelFaker
    from your_app.models import User
    from your_app.database import session

    # Create 5 fake users with explicit session
    ModelFaker(User, session).create(5)

**Framework Integration:**

For applications using Flask, Django, or Tornado:

.. code-block:: python

    from sqlalchemy_fake_model import ModelFaker
    from your_app.models import User

    # Session is automatically detected
    ModelFaker(User).create(5)

Set-up Models
=============

Supported Data Types
--------------------

The `ModelFaker` module supports the following data types:

1. `String` - Generates random strings of varying lengths.
2. `Text` - Generates random text values of varying lengths.
3. `Integer` - Generates random integers within a specified range.
4. `Float` - Generates random floating-point numbers within a specified range.
5. `Boolean` - Generates random boolean values.
6. `Date` - Generates random date values within a specified range.
7. `DateTime` - Generates random datetime values within a specified range.
8. `Enum` - Generates random values from a specified list of choices.
9. `Relationship` - Generates random values for relationships between models.
10. `Json` - Generates random data in the custom json format.


Default values
--------------

The `ModelFaker` module also supports default values for fields. These values will be used if no other value is specified.

Example implementation of default values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following example would result in a default value of `0` for the field:

.. code-block:: python

    is_deleted: Column[Boolean] = db.Column(
        db.Boolean,
        nullable=False,
        server_default="0"
    )

You can use default or server_default to set default values for fields.


Nullable fields
---------------

The `ModelFaker` module supports nullable fields. If a field is nullable, it will generate `None` values for that field.

Example implementation of nullable fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following example would result in a `None` value for the field:

.. code-block:: python

    description: Column[String] = db.Column(
        db.String(255),
        nullable=True
    )

Define max and min values
-------------------------

The `ModelFaker` module supports max and min values for fields. You can define the range of values for integer and float fields.

Example implementation of max and min values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following example would result in a random integer value between 1 and 100:

.. code-block:: python

    age: Column[Integer] = db.Column(
        db.Integer(),
        nullable=False,
        info='{"min": 1, "max": 100}'
    )

Define enum fields
------------------

The `ModelFaker` module supports enum fields. You can define a list of choices for an enum field,
and it will generate random values from that list.

Example implementation of enum field
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following example would result in a random value from the list of choices:

.. code-block:: python

    status: Column[Enum] = db.Column(
        Enum(StatusTypesEnum),
        nullable=False
    )

The enum class `StatusTypesEnum` could look like this:

.. code-block:: python

    from enum import Enum

    class StatusTypesEnum(Enum):

        CREATED = "created"

        PUBLISHED = "published"

        CANCELED = "canceled"

It also allows a default enum value:

.. code-block:: python

    status: Column[Enum] = db.Column(
        Enum(StatusTypesEnum),
        nullable=False,
        default=StatusTypesEnum.ACTIVE.value
    )

Define relationships
--------------------

ModelFaker automatically handles relationships between models, creating the necessary related records
to maintain referential integrity. It supports all SQLAlchemy relationship types:

- **OneToOne** - Creates one related record
- **OneToMany** - Creates multiple related records
- **ManyToMany** - Creates and links multiple records through association tables

**Example - User with Messages:**

.. code-block:: python

    class User(Base):
        __tablename__ = "users"

        id: Column[Integer] = Column(Integer, primary_key=True)
        name: Column[String] = Column(String(100))
        messages = relationship("Message", back_populates="user")

    class Message(Base):
        __tablename__ = "messages"

        id: Column[Integer] = Column(Integer, primary_key=True)
        content: Column[String] = Column(String(500))
        user_id: Column[Integer] = Column(Integer, ForeignKey("users.id"))
        user = relationship("User", back_populates="messages")

    # This automatically creates users for each message
    ModelFaker(Message).create(10)

**Note:** Different primary key types (UUID, String, etc.) are fully supported.

Define custom data format
-------------------------

The `ModelFaker` module supports custom data format generation. You can define custom functions to generate data for fields.

Example implementation of custom data format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following example would result in a json list of strings eg. string[] in the database:

.. code-block:: python

    emails: Column[Text] = db.Column(
        db.Text(),
        nullable=False,
        default='[]',
        doc='["string"], ["integer"]'
    )

Another example would result in a json object eg. object in the database:

.. code-block:: python

    address: Column[Text] = db.Column(
        db.Text(),
        nullable=False,
        default='{}',
        doc='{"street": "string", "location": {"city": ""string", "zip": "string"}}'
    )

Supported Frameworks
====================

ModelFaker provides seamless integration with popular web frameworks by automatically
detecting and using their SQLAlchemy sessions:

**Supported Frameworks:**

- **Flask** - Flask-SQLAlchemy integration
- **Django** - Django ORM integration
- **Tornado** - Tornado SQLAlchemy integration

**How it works:**

When using supported frameworks, ModelFaker automatically detects the current session
context, eliminating the need to manually pass session objects:

.. code-block:: python

    # In a Flask application
    @app.route('/seed-data')
    def seed_data():
        # No session needed - automatically detected
        ModelFaker(User).create(100)
        return "Data seeded successfully!"

**Manual Session:**

For other frameworks or custom setups, pass the session explicitly:

.. code-block:: python

    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=engine)
    session = Session()

    ModelFaker(User, session).create(100)
