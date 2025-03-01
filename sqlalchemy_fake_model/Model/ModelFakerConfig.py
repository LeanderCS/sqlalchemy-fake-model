from dataclasses import dataclass


@dataclass
class ModelFakerConfig:
    """
    Configuration for the ModelFaker class.

    :param fill_nullable_fields: Whether to fill nullable fields
        with fake data.
    :param fill_default_fields: Whether to fill default fields with fake data.
    """

    fill_nullable_fields: bool = False
    fill_default_fields: bool = False
