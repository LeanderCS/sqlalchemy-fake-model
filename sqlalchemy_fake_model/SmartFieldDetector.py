from typing import Any, Optional

from faker import Faker
from sqlalchemy import Column

from .Enum.ModelColumnTypesEnum import ModelColumnTypesEnum


class SmartFieldDetector:
    """
    Smart field detector that generates realistic data based on field names.
    """

    def __init__(self, faker: Faker):
        self.faker = faker

    def detect_and_generate(self, column: Column) -> Optional[Any]:
        """
        Detects field purpose based on name and generates appropriate data.
        Returns None if no smart detection is possible.
        """
        field_name = column.name.lower()
        column_type = column.type

        # Email fields (specific patterns only)
        if (field_name == "email" or
            field_name.endswith("_email") or
            field_name == "email_address" or
            (field_name.startswith("email_") and field_name in ["email_addr", "email_id"])):
            return self.faker.email()

        # Name fields (specific patterns first, then general)
        if "first_name" in field_name or "firstname" in field_name:
            return self.faker.first_name()
        if "last_name" in field_name or "lastname" in field_name:
            return self.faker.last_name()
        if (field_name in ["name", "full_name", "fullname"] or
            field_name in ["display_name", "user_name", "real_name", "person_name"]):
            return self.faker.name()

        # Address fields
        if "address" in field_name:
            return self.faker.address()
        if "street" in field_name:
            return self.faker.street_address()
        if "city" in field_name:
            return self.faker.city()
        if "state" in field_name:
            return self.faker.state()
        if field_name in ["zip", "zipcode", "postal_code", "postcode"]:
            return self.faker.zipcode()
        if "country" in field_name:
            return self.faker.country()

        # Phone fields
        if "phone" in field_name or "tel" in field_name:
            return self.faker.phone_number()

        # URL fields
        if "url" in field_name or "website" in field_name:
            return self.faker.url()

        # Company fields
        if "company" in field_name or "organization" in field_name:
            return self.faker.company()

        # Title/Job fields
        if "title" in field_name or "job" in field_name:
            return self.faker.job()

        # Description/Bio fields
        if (
            "description" in field_name
            or "bio" in field_name
            or "about" in field_name
        ):
            return self.faker.text(max_nb_chars=500)

        # Username fields
        if "username" in field_name or "user_name" in field_name:
            return self.faker.user_name()

        # Password fields (hashed)
        if "password" in field_name:
            return self.faker.sha256()

        # Date/Time specific fields
        if "birth" in field_name or "born" in field_name:
            return self.faker.date_of_birth()
        if "created" in field_name or "updated" in field_name:
            return self.faker.date_time_this_year()

        # Price/Money fields
        if (
            "price" in field_name
            or "cost" in field_name
            or "amount" in field_name
        ):
            if isinstance(column_type, ModelColumnTypesEnum.DECIMAL.value):
                return self.faker.pydecimal(
                    left_digits=5, right_digits=2, positive=True
                )
            return self.faker.pyfloat(
                left_digits=5, right_digits=2, positive=True
            )

        # Age fields
        if "age" in field_name:
            return self.faker.random_int(min=1, max=100)

        # Score/Rating fields
        if "score" in field_name or "rating" in field_name:
            return self.faker.random_int(min=1, max=10)

        return None
