from enum import Enum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    Interval,
    LargeBinary,
    String,
    Text,
    Time,
)
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSON, JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import DECIMAL

try:
    from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
except ImportError:
    PostgreSQLUUID = None


class ModelColumnTypesEnum(Enum):
    """Enum class for the model column types"""

    STRING = String

    INTEGER = Integer

    FLOAT = Float

    TEXT = Text

    BOOLEAN = Boolean

    DATETIME = DateTime

    DATE = Date

    TIME = Time

    INTERVAL = Interval

    DECIMAL = DECIMAL

    LARGEBINARY = LargeBinary

    UUID = UUID if PostgreSQLUUID else String

    JSON = JSON

    JSONB = JSONB

    ENUM = SQLAlchemyEnum

    RELATIONSHIP = relationship
