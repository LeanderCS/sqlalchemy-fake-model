from dataclasses import dataclass
from typing import Callable, Dict, Optional

from faker import Faker


@dataclass
class ModelFakerConfig:
    """
    Configuration for the ModelFaker class.

    :param fill_nullable_fields: Whether to fill nullable fields
        with fake data.
    :param fill_default_fields: Whether to fill default fields with fake data.
    :param locale: Locale for Faker (e.g., 'en_US', 'de_DE', 'fr_FR').
    :param seed: Seed for reproducible fake data generation.
    :param unique_constraints: Whether to enforce unique constraints.
    :param max_retries: Maximum retries for unique constraint violations.
    :param bulk_size: Number of records to insert in a single batch.
    :param field_overrides: Custom generators for specific fields.
    :param smart_detection: Enable smart field name detection for realistic
        data.
    :param faker_instance: Custom Faker instance to use.
    """

    fill_nullable_fields: bool = False
    fill_default_fields: bool = False
    locale: str = "en_US"
    seed: Optional[int] = None
    unique_constraints: bool = True
    max_retries: int = 10
    bulk_size: int = 1000
    field_overrides: Optional[Dict[str, Callable]] = None
    smart_detection: bool = True
    faker_instance: Optional[Faker] = None

    def __post_init__(self):
        if self.field_overrides is None:
            self.field_overrides = {}

        if self.faker_instance is None:
            self.faker_instance = Faker(self.locale)
            if self.seed is not None:
                self.faker_instance.seed_instance(self.seed)
