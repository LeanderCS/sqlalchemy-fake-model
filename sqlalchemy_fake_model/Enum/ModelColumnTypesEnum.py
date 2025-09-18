from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship


class ModelColumnTypesEnum(Enum):
    """Enum class for the model column types"""

    STRING = String

    INTEGER = Integer

    FLOAT = Float

    TEXT = Text

    BOOLEAN = Boolean

    DATETIME = DateTime

    DATE = Date

    ENUM = SQLAlchemyEnum

    RELATIONSHIP = relationship
