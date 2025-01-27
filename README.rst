sqlalchemy-fake-model
=====================

``ModelFaker`` is a utility that generates fake data for SQLAlchemy models.
It leverages the power of the Faker library to create realistic yet random data that can be used
to populate your database during development or for testing your application's functionality.

It supports a wide range of data types, including basic types, enums, and relationships between models.

Thank you for using ``sqlalchemy-fake-model``!
==============================================

If you have any questions or suggestions, please feel free to open an issue on GitHub `here <https://github.com/LeanderCS/sqlalchemy-fake-model>`__.

If you don't want to miss any updates, please star the repository.
This will help me to understand how many people are interested in this project.

:Test Status:

    .. image:: https://img.shields.io/github/actions/workflow/status/LeanderCS/sqlalchemy-fake-model/test.yaml?branch=main&style=flat-square&label=Github%20Actions
        :target: https://github.com/LeanderCS/sqlalchemy-fake-model/actions
    .. image:: https://img.shields.io/coveralls/LeanderCS/sqlalchemy-fake-model/main.svg?style=flat-square&label=Coverage
        :target: https://coveralls.io/r/LeanderCS/sqlalchemy-fake-model

:Version Info:

    .. image:: https://img.shields.io/pypi/v/sqlalchemy-fake-model?style=flat-square&label=PyPI
        :target: https://pypi.org/project/sqlalchemy-fake-model/

:Compatibility:

    .. image:: https://img.shields.io/pypi/pyversions/sqlalchemy-fake-model?style=flat-square&label=PyPI
        :target: https://pypi.org/project/sqlalchemy-fake-model/

.. :Downloads:

..    .. image:: https://img.shields.io/pypi/dm/sqlalchemy-fake-model?style=flat-square&label=PyPI
..        :target: https://pypi.org/project/sqlalchemy-fake-model/
..    .. image:: https://static.pepy.tech/badge/sqlalchemy-fake-model
..        :target: https://pypi.org/project/sqlalchemy-fake-model/

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

For all type of appications:

.. code-block:: python

    from sqlalchemy_fake_model import ModelFaker
    from path-to-model import Users
    from path-to-session import session

    ModelFaker(Users, session).create(5)

For appications using one of the `Supported Frameworks`_:

.. code-block:: python

    from sqlalchemy_fake_model import ModelFaker
    from path-to-model import Users

    ModelFaker(Users).create(5)

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

The `ModelFaker` module supports relationships between models. You can define relationships between models,
and it will generate the corresponding other part of those relationship.

It supports the following relationship types:

1. `OneToOne` - Generates random values for a one-to-one relationship.
2. `OneToMany` - Generates random values for a one-to-many relationship.
3. `ManyToMany` - Generates random values for a many-to-many relationship.

Example implementation of relationships
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following example would result in a creation of an entry for the users table to set up the relationship:

.. code-block:: python

    user_id: Column[Integer] = db.Column(
        db.Integer(),
        db.ForeignKey("users.id"),
        nullable=False
    )

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
--------------------

The `ModelFaker` module is able to detect the sqlalchemy session
automatically for the following frameworks:

1. `Flask`
2. `Django`
3. `Torando`

If you are using one of these frameworks, you can simply leave the session empty and
the module will try to get thesession from the framework.
If not you have to pass the db session as a parameter.
