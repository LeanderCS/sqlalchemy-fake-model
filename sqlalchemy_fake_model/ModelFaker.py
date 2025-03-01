import json
import random
import traceback
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

from faker import Faker
from sqlalchemy import Column, ColumnDefault, Table
from sqlalchemy.orm import ColumnProperty, Session

from .Enum.ModelColumnTypesEnum import ModelColumnTypesEnum
from .Error.InvalidAmountError import InvalidAmountError
from .Model.ModelFakerConfig import ModelFakerConfig


class ModelFaker:
    """
    The ModelFaker class is a utility class that helps in generating fake data
    for a given SQLAlchemy model. It uses the faker library to generate fake
    data based on the column types of the model. It also handles relationships
    between models and can generate data for different relationships.
    """

    def __init__(
        self,
        model: Union[Table, ColumnProperty],
        db: Optional[Session] = None,
        faker: Optional[Faker] = None,
        config: Optional[ModelFakerConfig] = None,
    ) -> None:
        """
        Initializes the ModelFaker class with the given model,
        database session, faker instance, and configuration.

        :param model: The SQLAlchemy model for which fake data
            needs to be generated.
        :param db: Optional SQLAlchemy session to be used for
            creating fake data.
        :param faker: Optional Faker instance to be used for
            generating fake data.
        :param config: Optional ModelFakerConfig instance to be
            used for configuring the ModelFaker.
        """
        self.model = model
        self.db = db or self._get_framework_session()
        self.faker = faker or Faker()
        self.config = config or ModelFakerConfig()

    @staticmethod
    def _get_framework_session() -> Optional[Session]:
        """
        Tries to get the SQLAlchemy session from available frameworks.

        :return: The SQLAlchemy session if available.
        :raises RuntimeError: If no supported framework
            is installed or configured
        """
        try:
            from flask import current_app

            return current_app.extensions["sqlalchemy"].db.session
        except (ImportError, KeyError):
            pass

        try:
            from tornado.web import Application

            return Application().settings["db"]
        except (ImportError, KeyError):
            pass

        try:
            from django.conf import settings
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            engine = create_engine(settings.DATABASES["default"]["ENGINE"])
            return sessionmaker(bind=engine)()
        except (ImportError, KeyError, AttributeError):
            pass

        raise RuntimeError(
            "No SQLAlchemy session provided and no supported framework "
            "installed or configured."
        )

    def create(self, amount: Optional[int] = 1) -> None:
        """
        Creates the specified amount of fake data entries for the model.
        It handles exceptions and rolls back the session
        in case of any errors.

        :param amount: The number of fake data entries to create.
        :raises InvalidAmountError: If the amount is not an integer.
        """
        if not isinstance(amount, int):
            raise InvalidAmountError(amount)

        try:
            for _ in range(amount):
                data = {}

                for column in self.__getTableColumns():
                    if self.__shouldSkipField(column):
                        continue

                    data[column.name] = self._generateFakeData(column)

                if self.__isManyToManyRelationTable():
                    self.db.execute(self.model.insert().values(**data))

                else:
                    self.db.add(self.model(**data))

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise RuntimeError(
                f"Failed to commit: {e} {traceback.format_exc()}"
            )

    def _generateFakeData(
        self, column: Column
    ) -> Optional[Union[str, int, bool, date, datetime, None]]:
        """
        Generates fake data for a given column based on its type.
        It handles Enum, String, Integer, Boolean, DateTime, and Date column
        types.

        :param column: The SQLAlchemy column for which fake data
            needs to be generated.
        :return: The fake data generated for the column.
        """
        columnType = column.type

        if column.doc:
            return str(self._generateJsonData(column.doc))

        # Enum has to be the first type to check, or otherwise it
        # uses the options of the corresponding type of the enum options
        elif isinstance(columnType, ModelColumnTypesEnum.ENUM.value):
            return random.choice(columnType.enums)

        elif column.foreign_keys:
            related_attribute = list(column.foreign_keys)[0].column.name
            return getattr(
                self.__handleRelationship(column), related_attribute
            )

        elif column.primary_key:
            return self._generatePrimitive(columnType)

        elif isinstance(columnType, ModelColumnTypesEnum.STRING.value):
            maxLength = (
                columnType.length if hasattr(columnType, "length") else 255
            )
            return self.faker.text(max_nb_chars=maxLength)

        elif isinstance(columnType, ModelColumnTypesEnum.INTEGER.value):
            info = column.info
            if not info:
                return self.faker.random_int()

            min_value = column.info.get("min", 1)
            max_value = column.info.get("max", 100)
            return self.faker.random_int(min=min_value, max=max_value)

        elif isinstance(columnType, ModelColumnTypesEnum.FLOAT.value):
            precision = getattr(columnType, "precision")
            if not precision:
                return self.faker.pyfloat()

            max_value = 10 ** (precision[0] - precision[1]) - 1
            return round(
                self.faker.pyfloat(min_value=0, max_value=max_value),
                precision[1],
            )

        elif isinstance(columnType, ModelColumnTypesEnum.BOOLEAN.value):
            return self.faker.boolean()

        elif isinstance(columnType, ModelColumnTypesEnum.DATE.value):
            return self.faker.date_object()

        elif isinstance(columnType, ModelColumnTypesEnum.DATETIME.value):
            return self.faker.date_time()

        return None

    def __handleRelationship(self, column: Column) -> Optional[Table]:
        """
        Handles the relationship of a column with another model.
        It creates a fake data entry for the parent model and returns its id.
        """
        parentModel = self.__getRelatedClass(column)

        ModelFaker(parentModel, self.db).create()

        return self.db.query(parentModel).first()

    def __isManyToManyRelationTable(self) -> bool:
        """
        Checks if the model is a many-to-many relationship table.
        """
        return not hasattr(self.model, "__table__") and not hasattr(
            self.model, "__mapper__"
        )

    def __shouldSkipField(self, column: Column) -> bool:
        """
        Checks if a column is a primary key or has a default value.
        """
        return (
            (column.primary_key and self.__isFieldAutoIncrement(column))
            or self.__hasFieldDefaultValue(column)
            or self.__isFieldNullable(column)
        )

    @staticmethod
    def __isFieldAutoIncrement(column: Column) -> bool:
        """
        Checks if a column is autoincrement.
        """
        return column.autoincrement and isinstance(
            column.type, ModelColumnTypesEnum.INTEGER.value
        )

    def __hasFieldDefaultValue(self, column: Column) -> bool:
        """
        Checks if a column has a default value.
        """
        return (
            isinstance(column.default, ColumnDefault)
            and column.default.arg is not None
            and not self.config.fill_default_fields
        )

    def __isFieldNullable(self, column: Column) -> bool:
        """
        Checks if a column is nullable.
        """
        return (
            column.nullable is not None
            and column.nullable is True
            and not self.config.fill_nullable_fields
        )

    def __getTableColumns(self) -> List[Column]:
        """
        Returns the columns of the model's table.
        """
        return (
            self.model.columns
            if self.__isManyToManyRelationTable()
            else self.model.__table__.columns
        )

    def __getRelatedClass(self, column: Column) -> Table:
        """
        Returns the related class of a column if it has
        a relationship with another model.
        """
        if (
            not self.__isManyToManyRelationTable()
            and column.name in self.model.__mapper__.relationships.keys()
        ):
            return self.model.__mapper__.relationships[
                column.key
            ].mapper.class_

        fk = list(column.foreign_keys)[0]

        return fk.column.table

    def _generateJsonData(self, docstring: str) -> Dict[str, Any]:
        """
        Generates JSON data based on the provided docstring.
        """
        json_structure = json.loads(docstring)

        return self._populateJsonStructure(json_structure)

    def _populateJsonStructure(
        self, structure: Union[Dict[str, Any], List[Any]]
    ) -> Any:
        """
        Populates the JSON structure with fake data based on the defined
        schema.
        """
        if isinstance(structure, dict):
            return {
                key: self._populateJsonStructure(value)
                if isinstance(value, (dict, list))
                else self._generatePrimitive(value)
                for key, value in structure.items()
            }

        elif isinstance(structure, list):
            return [
                self._populateJsonStructure(item)
                if isinstance(item, (dict, list))
                else self._generatePrimitive(item)
                for item in structure
            ]

        return structure

    def _generatePrimitive(self, primitive_type: str) -> Any:
        """
        Generates fake data for primitive types.
        """
        if primitive_type == "boolean":
            return self.faker.boolean()
        elif primitive_type == "datetime":
            return self.faker.date_time().isoformat()
        elif primitive_type == "date":
            return self.faker.date()
        elif primitive_type == "integer":
            return self.faker.random_int()
        elif primitive_type == "string":
            return self.faker.word()
        elif primitive_type == "float":
            return self.faker.pyfloat()
        return self.faker.word()
