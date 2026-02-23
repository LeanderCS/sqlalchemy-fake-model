"""
Test the SmartFieldDetector class
"""
import pytest
from faker import Faker
from sqlalchemy import Column, String, Integer, Float, Date, DateTime
from sqlalchemy.types import DECIMAL
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy_fake_model import SmartFieldDetector

Base = declarative_base()


@pytest.fixture
def smart_detector() -> SmartFieldDetector:
    """Fixture to create a SmartFieldDetector instance."""
    faker = Faker('en_US')
    faker.seed_instance(12345)  # For reproducible tests
    return SmartFieldDetector(faker)


class TestEmailFields:
    """Test email field detection."""

    def test_email_field(self, smart_detector):
        """Test standard email field."""
        column = Column('email', String(255))
        result = smart_detector.detect_and_generate(column)
        assert '@' in result
        assert '.' in result

    def test_email_address_field(self, smart_detector):
        """Test email_address field variant."""
        column = Column('email_address', String(255))
        result = smart_detector.detect_and_generate(column)
        assert '@' in result

    def test_user_email_field(self, smart_detector):
        """Test user_email field variant."""
        column = Column('user_email', String(255))
        result = smart_detector.detect_and_generate(column)
        assert '@' in result

    def test_work_email_field(self, smart_detector):
        """Test work_email field variant."""
        column = Column('work_email', String(255))
        result = smart_detector.detect_and_generate(column)
        assert '@' in result


class TestNameFields:
    """Test name field detection."""

    def test_name_field(self, smart_detector):
        """Test standard name field."""
        column = Column('name', String(100))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_full_name_field(self, smart_detector):
        """Test full_name field."""
        column = Column('full_name', String(100))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)
        assert ' ' in result  # Should contain space for full name

    def test_fullname_field(self, smart_detector):
        """Test fullname field (no underscore)."""
        column = Column('fullname', String(100))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_first_name_field(self, smart_detector):
        """Test first_name field."""
        column = Column('first_name', String(50))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_firstname_field(self, smart_detector):
        """Test firstname field (no underscore)."""
        column = Column('firstname', String(50))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_last_name_field(self, smart_detector):
        """Test last_name field."""
        column = Column('last_name', String(50))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_lastname_field(self, smart_detector):
        """Test lastname field (no underscore)."""
        column = Column('lastname', String(50))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_display_name_field(self, smart_detector):
        """Test display_name field."""
        column = Column('display_name', String(100))
        result = smart_detector.detect_and_generate(column)
        # display_name contains 'name' so it should be detected
        assert isinstance(result, str)


class TestAddressFields:
    """Test address field detection."""

    def test_address_field(self, smart_detector):
        """Test standard address field."""
        column = Column('address', String(255))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_street_field(self, smart_detector):
        """Test street field."""
        column = Column('street', String(255))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_street_address_field(self, smart_detector):
        """Test street_address field."""
        column = Column('street_address', String(255))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_city_field(self, smart_detector):
        """Test city field."""
        column = Column('city', String(100))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_state_field(self, smart_detector):
        """Test state field."""
        column = Column('state', String(50))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_zip_field(self, smart_detector):
        """Test zip field."""
        column = Column('zip', String(10))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_zipcode_field(self, smart_detector):
        """Test zipcode field."""
        column = Column('zipcode', String(10))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_postal_code_field(self, smart_detector):
        """Test postal_code field."""
        column = Column('postal_code', String(10))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_postcode_field(self, smart_detector):
        """Test postcode field."""
        column = Column('postcode', String(10))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_country_field(self, smart_detector):
        """Test country field."""
        column = Column('country', String(100))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_billing_address_field(self, smart_detector):
        """Test billing_address field."""
        column = Column('billing_address', String(255))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)


class TestPhoneFields:
    """Test phone field detection."""

    def test_phone_field(self, smart_detector):
        """Test standard phone field."""
        column = Column('phone', String(20))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_phone_number_field(self, smart_detector):
        """Test phone_number field."""
        column = Column('phone_number', String(20))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_tel_field(self, smart_detector):
        """Test tel field."""
        column = Column('tel', String(20))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_telephone_field(self, smart_detector):
        """Test telephone field."""
        column = Column('telephone', String(20))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_mobile_field(self, smart_detector):
        """Test mobile field."""
        column = Column('mobile_phone', String(20))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)


class TestUrlFields:
    """Test URL field detection."""

    def test_url_field(self, smart_detector):
        """Test standard url field."""
        column = Column('url', String(255))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)
        assert result.startswith(('http://', 'https://'))

    def test_website_field(self, smart_detector):
        """Test website field."""
        column = Column('website', String(255))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)
        assert result.startswith(('http://', 'https://'))

    def test_homepage_field(self, smart_detector):
        """Test homepage field."""
        column = Column('homepage_url', String(255))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_profile_url_field(self, smart_detector):
        """Test profile_url field."""
        column = Column('profile_url', String(255))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)


class TestCompanyFields:
    """Test company field detection."""

    def test_company_field(self, smart_detector):
        """Test standard company field."""
        column = Column('company', String(200))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_organization_field(self, smart_detector):
        """Test organization field."""
        column = Column('organization', String(200))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_company_name_field(self, smart_detector):
        """Test company_name field."""
        column = Column('company_name', String(200))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_employer_field(self, smart_detector):
        """Test employer field."""
        column = Column('employer_company', String(200))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)


class TestJobTitleFields:
    """Test job/title field detection."""

    def test_title_field(self, smart_detector):
        """Test standard title field."""
        column = Column('title', String(100))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_job_field(self, smart_detector):
        """Test job field."""
        column = Column('job', String(100))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_job_title_field(self, smart_detector):
        """Test job_title field."""
        column = Column('job_title', String(100))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_position_field(self, smart_detector):
        """Test position field."""
        column = Column('job_position', String(100))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)


class TestDescriptionFields:
    """Test description field detection."""

    def test_description_field(self, smart_detector):
        """Test standard description field."""
        column = Column('description', String(500))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)
        assert len(result) > 0
        assert len(result) <= 500

    def test_bio_field(self, smart_detector):
        """Test bio field."""
        column = Column('bio', String(500))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)
        assert len(result) <= 500

    def test_about_field(self, smart_detector):
        """Test about field."""
        column = Column('about', String(500))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_summary_field(self, smart_detector):
        """Test summary field."""
        column = Column('description_summary', String(500))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)


class TestUsernameFields:
    """Test username field detection."""

    def test_username_field(self, smart_detector):
        """Test standard username field."""
        column = Column('username', String(50))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_user_name_field(self, smart_detector):
        """Test user_name field."""
        column = Column('user_name', String(50))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_login_field(self, smart_detector):
        """Test login field."""
        column = Column('login_username', String(50))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)


class TestPasswordFields:
    """Test password field detection."""

    def test_password_field(self, smart_detector):
        """Test standard password field."""
        column = Column('password', String(255))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)
        assert len(result) == 64  # SHA256 hash length

    def test_password_hash_field(self, smart_detector):
        """Test password_hash field."""
        column = Column('password_hash', String(255))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)
        assert len(result) == 64

    def test_user_password_field(self, smart_detector):
        """Test user_password field."""
        column = Column('user_password', String(255))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)


class TestDateTimeFields:
    """Test date/time field detection."""

    def test_birth_field(self, smart_detector):
        """Test birth field."""
        column = Column('birth', Date)
        result = smart_detector.detect_and_generate(column)
        assert result is not None

    def test_birthday_field(self, smart_detector):
        """Test birthday field."""
        column = Column('birth_date', Date)
        result = smart_detector.detect_and_generate(column)
        assert result is not None

    def test_born_field(self, smart_detector):
        """Test born field."""
        column = Column('born', Date)
        result = smart_detector.detect_and_generate(column)
        assert result is not None

    def test_created_field(self, smart_detector):
        """Test created field."""
        column = Column('created', DateTime)
        result = smart_detector.detect_and_generate(column)
        assert result is not None

    def test_created_at_field(self, smart_detector):
        """Test created_at field."""
        column = Column('created_at', DateTime)
        result = smart_detector.detect_and_generate(column)
        assert result is not None

    def test_updated_field(self, smart_detector):
        """Test updated field."""
        column = Column('updated', DateTime)
        result = smart_detector.detect_and_generate(column)
        assert result is not None

    def test_updated_at_field(self, smart_detector):
        """Test updated_at field."""
        column = Column('updated_at', DateTime)
        result = smart_detector.detect_and_generate(column)
        assert result is not None


class TestPriceMoneyFields:
    """Test price/money field detection."""

    def test_price_field_decimal(self, smart_detector):
        """Test price field with decimal type."""
        column = Column('price', DECIMAL(10, 2))
        result = smart_detector.detect_and_generate(column)
        assert result is not None
        assert result >= 0

    def test_price_field_float(self, smart_detector):
        """Test price field with float type."""
        column = Column('price', Float)
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, float)
        assert result >= 0

    def test_cost_field(self, smart_detector):
        """Test cost field."""
        column = Column('cost', Float)
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, float)
        assert result >= 0

    def test_amount_field(self, smart_detector):
        """Test amount field."""
        column = Column('amount', DECIMAL(10, 2))
        result = smart_detector.detect_and_generate(column)
        assert result is not None
        assert result >= 0

    def test_total_price_field(self, smart_detector):
        """Test total_price field."""
        column = Column('total_price', Float)
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, float)

    def test_unit_cost_field(self, smart_detector):
        """Test unit_cost field."""
        column = Column('unit_cost', Float)
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, float)


class TestNumericFields:
    """Test numeric field detection."""

    def test_age_field(self, smart_detector):
        """Test age field."""
        column = Column('age', Integer)
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, int)
        assert 1 <= result <= 100

    def test_user_age_field(self, smart_detector):
        """Test user_age field."""
        column = Column('user_age', Integer)
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, int)
        assert 1 <= result <= 100

    def test_score_field(self, smart_detector):
        """Test score field."""
        column = Column('score', Integer)
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, int)
        assert 1 <= result <= 10

    def test_rating_field(self, smart_detector):
        """Test rating field."""
        column = Column('rating', Integer)
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, int)
        assert 1 <= result <= 10

    def test_review_score_field(self, smart_detector):
        """Test review_score field."""
        column = Column('review_score', Integer)
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, int)

    def test_user_rating_field(self, smart_detector):
        """Test user_rating field."""
        column = Column('user_rating', Integer)
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, int)


class TestEdgeCases:
    """Test edge cases and non-matching fields."""

    def test_non_matching_field(self, smart_detector):
        """Test field that doesn't match any pattern."""
        column = Column('random_field', String(100))
        result = smart_detector.detect_and_generate(column)
        assert result is None

    def test_partial_match_not_triggered(self, smart_detector):
        """Test that partial matches don't trigger detection."""
        column = Column('email_like_but_not', String(100))
        result = smart_detector.detect_and_generate(column)
        assert result is None

    def test_case_insensitive_matching(self, smart_detector):
        """Test that field detection is case insensitive."""
        column = Column('EMAIL', String(255))
        result = smart_detector.detect_and_generate(column)
        assert '@' in result

    def test_mixed_case_field(self, smart_detector):
        """Test mixed case field names."""
        column = Column('FirstName', String(50))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_camel_case_field(self, smart_detector):
        """Test camelCase field names."""
        column = Column('phoneNumber', String(20))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_empty_field_name(self, smart_detector):
        """Test empty field name."""
        column = Column('', String(100))
        result = smart_detector.detect_and_generate(column)
        assert result is None

    def test_numeric_field_name(self, smart_detector):
        """Test numeric field name."""
        column = Column('123', String(100))
        result = smart_detector.detect_and_generate(column)
        assert result is None

    def test_special_characters_field_name(self, smart_detector):
        """Test field name with special characters."""
        column = Column('field@name', String(100))
        result = smart_detector.detect_and_generate(column)
        assert result is None

    def test_very_long_field_name(self, smart_detector):
        """Test very long field name."""
        long_name = 'a' * 1000 + '_email'
        column = Column(long_name, String(255))
        result = smart_detector.detect_and_generate(column)
        assert '@' in result  # Should still detect email


class TestFieldCombinations:
    """Test fields with multiple possible matches."""

    def test_email_address_field_priority(self, smart_detector):
        """Test field that could match multiple patterns."""
        # This should match email pattern, not address pattern
        column = Column('email_address', String(255))
        result = smart_detector.detect_and_generate(column)
        assert '@' in result

    def test_birth_date_field(self, smart_detector):
        """Test field with birth and date."""
        column = Column('birth_date', Date)
        result = smart_detector.detect_and_generate(column)
        assert result is not None

    def test_company_phone_field(self, smart_detector):
        """Test field that matches company and phone."""
        # Should match phone pattern first
        column = Column('company_phone', String(20))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)

    def test_user_title_field(self, smart_detector):
        """Test field that could match title pattern."""
        column = Column('user_title', String(100))
        result = smart_detector.detect_and_generate(column)
        assert isinstance(result, str)


class TestLocaleConsistency:
    """Test that different locales work consistently."""

    def test_different_locale(self):
        """Test SmartFieldDetector with different locale."""
        faker = Faker('de_DE')
        detector = SmartFieldDetector(faker)

        column = Column('email', String(255))
        result = detector.detect_and_generate(column)
        assert '@' in result
        assert '.' in result

    def test_multiple_locales(self):
        """Test multiple locales produce valid results."""
        locales = ['en_US', 'de_DE', 'fr_FR', 'es_ES']

        for locale in locales:
            faker = Faker(locale)
            detector = SmartFieldDetector(faker)

            # Test basic email generation
            column = Column('email', String(255))
            result = detector.detect_and_generate(column)
            assert '@' in result

            # Test name generation
            column = Column('name', String(100))
            result = detector.detect_and_generate(column)
            assert isinstance(result, str)
            assert len(result) > 0


class TestPerformance:
    """Test performance characteristics."""

    def test_detection_speed(self, smart_detector):
        """Test that detection is reasonably fast."""
        import time

        column = Column('email', String(255))

        start_time = time.time()
        for _ in range(1000):
            smart_detector.detect_and_generate(column)
        end_time = time.time()

        # Should complete 1000 detections in under 1 second
        assert (end_time - start_time) < 1.0

    def test_non_matching_speed(self, smart_detector):
        """Test that non-matching fields are handled quickly."""
        import time

        column = Column('random_field_name', String(100))

        start_time = time.time()
        for _ in range(1000):
            result = smart_detector.detect_and_generate(column)
            assert result is None
        end_time = time.time()

        # Should complete 1000 non-matches in under 0.5 seconds
        assert (end_time - start_time) < 0.5
