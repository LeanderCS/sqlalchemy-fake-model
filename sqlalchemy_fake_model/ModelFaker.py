import json
import logging
import random
import traceback
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

from faker import Faker
from sqlalchemy import Column, ColumnDefault, Table
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import ColumnProperty, Session

from .Enum.ModelColumnTypesEnum import ModelColumnTypesEnum
from .Error.InvalidAmountError import InvalidAmountError
from .Error.UniquenessError import UniquenessError
from .Model.ModelFakerConfig import ModelFakerConfig
from .SmartFieldDetector import SmartFieldDetector


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
        self.config = config or ModelFakerConfig()
        self.faker = (
            faker or self.config.faker_instance or Faker(self.config.locale)
        )
        self.logger = logging.getLogger(__name__)
        self._unique_values = {}
        self.smart_detector = (
            SmartFieldDetector(self.faker)
            if self.config.smart_detection
            else None
        )

        if self.config.seed is not None:
            self.faker.seed_instance(self.config.seed)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        if exc_type is not None:
            self.logger.error(f"Exception in ModelFaker context: {exc_val}")
            if hasattr(self.db, "rollback"):
                try:
                    self.db.rollback()
                    self.logger.info("Database transaction rolled back")
                except Exception as rollback_error:
                    self.logger.error(f"Failed to rollback: {rollback_error}")
        return False

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

        if amount <= self.config.bulk_size:
            self._create_single_batch(amount)
        else:
            self._create_bulk(amount)

    def _create_single_batch(self, amount: int) -> None:
        """Creates a single batch of records."""
        try:
            batch_data = []

            for _ in range(amount):
                data = {}
                for column in self.__get_table_columns():
                    if self.__should_skip_field(column):
                        continue
                    data[column.name] = (
                        self._generate_fake_data_with_overrides(column)
                    )
                batch_data.append(data)

            if self.__is_many_to_many_relation_table():
                self.db.execute(self.model.insert().values(batch_data))
            else:
                for data in batch_data:
                    self.db.add(self.model(**data))

            self.db.commit()
            self.logger.info(f"Successfully created {amount} records")

        except IntegrityError as e:
            self.db.rollback()
            self.logger.error(f"Integrity error in batch creation: {e}")
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                raise UniquenessError("unknown_field", self.config.max_retries)
            raise
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to create batch: {e}")
            raise RuntimeError(
                f"Failed to commit: {e} {traceback.format_exc()}"
            )

    def _create_bulk(self, amount: int) -> None:
        """Creates records in multiple batches for better performance."""
        remaining = amount
        created = 0

        while remaining > 0:
            batch_size = min(remaining, self.config.bulk_size)
            try:
                self._create_single_batch(batch_size)
                created += batch_size
                remaining -= batch_size
                self.logger.info(f"Created {created}/{amount} records")
            except Exception as e:
                self.logger.error(
                    f"Failed to create bulk batch at {created}/{amount}: {e}"
                )
                raise

    def _generate_fake_data(
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
        column_type = column.type

        if column.doc:
            return str(self._generate_json_data(column.doc))

        # Enum has to be the first type to check, or otherwise it
        # uses the options of the corresponding type of the enum options
        if isinstance(column_type, ModelColumnTypesEnum.ENUM.value):
            return random.choice(column_type.enums)

        if column.foreign_keys:
            related_attribute = list(column.foreign_keys)[0].column.name
            return getattr(
                self.__handle_relationship(column), related_attribute
            )

        if column.primary_key:
            return self._generate_primitive(column_type)

        if isinstance(column_type, ModelColumnTypesEnum.STRING.value):
            max_length = (
                column_type.length
                if hasattr(column_type, "length")
                and column_type.length is not None
                else 255
            )
            return self.faker.text(max_nb_chars=max_length)

        if isinstance(column_type, ModelColumnTypesEnum.INTEGER.value):
            info = column.info
            if not info:
                return self.faker.random_int()

            min_value = column.info.get("min", 1)
            max_value = column.info.get("max", 100)
            return self.faker.random_int(min=min_value, max=max_value)

        if isinstance(column_type, ModelColumnTypesEnum.FLOAT.value):
            precision = column_type.precision
            if not precision:
                return self.faker.pyfloat()

            max_value = 10 ** (precision[0] - precision[1]) - 1
            return round(
                self.faker.pyfloat(min_value=0, max_value=max_value),
                precision[1],
            )

        if isinstance(column_type, ModelColumnTypesEnum.BOOLEAN.value):
            return self.faker.boolean()

        if isinstance(column_type, ModelColumnTypesEnum.DATE.value):
            return self.faker.date_object()

        if isinstance(column_type, ModelColumnTypesEnum.DATETIME.value):
            return self.faker.date_time()

        if isinstance(column_type, ModelColumnTypesEnum.TIME.value):
            return self.faker.time_object()

        if isinstance(column_type, ModelColumnTypesEnum.UUID.value):
            return self.faker.uuid4()

        if isinstance(column_type, ModelColumnTypesEnum.DECIMAL.value):
            precision = getattr(column_type, "precision", None)
            scale = getattr(column_type, "scale", None)
            if precision and scale:
                max_digits = precision - scale
                max_value = 10**max_digits - 1
                return round(
                    self.faker.pyfloat(min_value=0, max_value=max_value), scale
                )
            return self.faker.pydecimal(
                left_digits=10, right_digits=2, positive=True
            )

        if isinstance(column_type, ModelColumnTypesEnum.INTERVAL.value):
            days = self.faker.random_int(min=1, max=365)
            return f"{days} days"

        if isinstance(column_type, ModelColumnTypesEnum.LARGEBINARY.value):
            return self.faker.binary(length=256)

        if isinstance(
            column_type,
            (
                ModelColumnTypesEnum.JSON.value,
                ModelColumnTypesEnum.JSONB.value,
            ),
        ):
            json_structure = {
                "id": "integer",
                "name": "string",
                "active": "boolean",
            }
            return self._populate_json_structure(json_structure)

        return None

    def __handle_relationship(self, column: Column) -> Optional[Table]:
        """
        Handles the relationship of a column with another model.
        It creates a fake data entry for the parent model and returns its id.
        """
        parent_model = self.__get_related_class(column)

        ModelFaker(parent_model, self.db).create()

        return self.db.query(parent_model).first()

    def __is_many_to_many_relation_table(self) -> bool:
        """
        Checks if the model is a many-to-many relationship table.
        """
        return not hasattr(self.model, "__table__") and not hasattr(
            self.model, "__mapper__"
        )

    def __should_skip_field(self, column: Column) -> bool:
        """
        Checks if a column is a primary key or has a default value.
        """
        return (
            (column.primary_key and self.__is_field_auto_increment(column))
            or self.__has_field_default_value(column)
            or self.__is_field_nullable(column)
        )

    @staticmethod
    def __is_field_auto_increment(column: Column) -> bool:
        """
        Checks if a column is autoincrement.
        """
        return column.autoincrement and isinstance(
            column.type, ModelColumnTypesEnum.INTEGER.value
        )

    def __has_field_default_value(self, column: Column) -> bool:
        """
        Checks if a column has a default value.
        """
        return (
            isinstance(column.default, ColumnDefault)
            and column.default.arg is not None
            and not self.config.fill_default_fields
        )

    def __is_field_nullable(self, column: Column) -> bool:
        """
        Checks if a column is nullable.
        """
        return (
            column.nullable is not None
            and column.nullable is True
            and not self.config.fill_nullable_fields
        )

    def __get_table_columns(self) -> List[Column]:
        """
        Returns the columns of the model's table.
        """
        return (
            self.model.columns
            if self.__is_many_to_many_relation_table()
            else self.model.__table__.columns
        )

    def __get_related_class(self, column: Column) -> Table:
        """
        Returns the related class of a column if it has
        a relationship with another model.
        """
        if (
            not self.__is_many_to_many_relation_table()
            and column.name in self.model.__mapper__.relationships
        ):
            return self.model.__mapper__.relationships[
                column.key
            ].mapper.class_

        fk = list(column.foreign_keys)[0]

        return fk.column.table

    def _generate_json_data(self, docstring: str) -> Dict[str, Any]:
        """
        Generates JSON data based on the provided docstring.
        """
        json_structure = json.loads(docstring)

        return self._populate_json_structure(json_structure)

    def _populate_json_structure(
        self, structure: Union[Dict[str, Any], List[Any]]
    ) -> Any:
        """
        Populates the JSON structure with fake data based on the defined
        schema.
        """
        if isinstance(structure, dict):
            return {
                key: self._populate_json_structure(value)
                if isinstance(value, (dict, list))
                else self._generate_primitive(value)
                for key, value in structure.items()
            }

        if isinstance(structure, list):
            return [
                self._populate_json_structure(item)
                if isinstance(item, (dict, list))
                else self._generate_primitive(item)
                for item in structure
            ]

        return structure

    def _generate_fake_data_with_overrides(self, column: Column) -> Any:
        """
        Generates fake data with custom overrides and optional smart detection.
        """
        if column.name in self.config.field_overrides:
            return self.config.field_overrides[column.name]()

        if self.smart_detector:
            smart_value = self.smart_detector.detect_and_generate(column)
            if smart_value is not None:
                return smart_value

        return self._generate_fake_data(column)

    def _generate_primitive(self, primitive_type: str) -> Any:
        """
        Generates fake data for primitive types.
        """
        if primitive_type == "boolean":
            return self.faker.boolean()
        if primitive_type == "datetime":
            return self.faker.date_time().isoformat()
        if primitive_type == "date":
            return self.faker.date()
        if primitive_type == "integer":
            return self.faker.random_int()
        if primitive_type == "string":
            return self.faker.word()
        if primitive_type == "float":
            return self.faker.pyfloat()
        return self.faker.word()

    def create_batch(self, amount: int, commit: bool = False) -> List[Any]:
        """
        Creates a batch of model instances without committing to database.

        :param amount: Number of instances to create
        :param commit: Whether to commit the batch to database
        :return: List of created model instances
        """
        if not isinstance(amount, int):
            raise InvalidAmountError(amount)

        instances = []
        try:
            for _ in range(amount):
                data = {}
                for column in self.__get_table_columns():
                    if self.__should_skip_field(column):
                        continue
                    data[column.name] = (
                        self._generate_fake_data_with_overrides(column)
                    )

                if not self.__is_many_to_many_relation_table():
                    instance = self.model(**data)
                    instances.append(instance)
                    if commit:
                        self.db.add(instance)

            if commit and instances:
                self.db.commit()
                self.logger.info(
                    f"Committed batch of {len(instances)} instances"
                )

            return instances

        except Exception as e:
            if commit:
                self.db.rollback()
            self.logger.error(f"Failed to create batch: {e}")
            raise

    def create_with(
        self, overrides: Dict[str, Any], amount: int = 1
    ) -> List[Any]:
        """
        Creates model instances with specific field overrides.

        :param overrides: Dictionary of field values to override
        :param amount: Number of instances to create
        :return: List of created model instances
        """
        if not isinstance(amount, int):
            raise InvalidAmountError(amount)

        instances = []
        try:
            for _ in range(amount):
                data = {}
                for column in self.__get_table_columns():
                    if self.__should_skip_field(column):
                        continue

                    if column.name in overrides:
                        data[column.name] = overrides[column.name]
                    else:
                        data[column.name] = (
                            self._generate_fake_data_with_overrides(column)
                        )

                if self.__is_many_to_many_relation_table():
                    self.db.execute(self.model.insert().values(**data))
                else:
                    instance = self.model(**data)
                    instances.append(instance)
                    self.db.add(instance)

            self.db.commit()
            self.logger.info(
                f"Created {len(instances)} instances with overrides"
            )
            return instances

        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to create with overrides: {e}")
            raise

    def reset(self, confirm: bool = False) -> int:
        """
        Removes all records from the model's table.

        :param confirm: Must be True to actually perform the deletion
        :return: Number of deleted records
        """
        if not confirm:
            raise ValueError("Must set confirm=True to delete all records")

        try:
            if self.__is_many_to_many_relation_table():
                result = self.db.execute(self.model.delete())
                deleted_count = result.rowcount
            else:
                deleted_count = self.db.query(self.model).count()
                self.db.query(self.model).delete()

            self.db.commit()
            self.logger.info(
                f"Deleted {deleted_count} records from {self.model}"
            )
            return deleted_count

        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to reset table: {e}")
            raise
