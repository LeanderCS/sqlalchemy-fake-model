Changelog
=========

All notable changes to this project will be documented in this file.

[0.1.0] - 2025-09-19
--------------------

Added
^^^^^

- Added support for python 3.14
**New Data Types Support:**
- UUID fields with automatic UUID generation
- JSON/JSONB fields with structured data generation
- DECIMAL fields with precision and scale support
- TIME fields for time-only values
- INTERVAL fields for time durations
- LARGEBINARY fields for binary data

**Smart Field Detection:**
- Intelligent field name recognition for realistic data generation
- Email fields automatically generate valid email addresses
- Name fields (first_name, last_name, full_name) generate realistic names
- Address fields generate complete addresses with street, city, state, country
- Phone fields generate valid phone numbers
- Company/organization fields generate business names
- URL/website fields generate valid URLs
- Price/amount/cost fields generate appropriate monetary values
- Age fields generate realistic age ranges
- Score/rating fields generate appropriate rating values
- Username fields generate valid usernames
- Password fields generate secure hashed passwords
- Date-specific fields (birth, created, updated) generate contextual dates

**Enhanced Configuration (ModelFakerConfig):**
- Locale support for multi-language data generation (e.g., 'en_US', 'de_DE', 'fr_FR')
- Seed functionality for reproducible test data generation
- Field-specific overrides with custom generator functions
- Unique constraint enforcement with configurable retry attempts
- Bulk insert configuration with customizable batch sizes
- Smart detection toggle for enabling/disabling intelligent field recognition
- Custom Faker instance support

**New Utility Methods:**
- ``create_batch(amount, commit=False)`` - Create model instances without immediate commit
- ``create_with(overrides, amount=1)`` - Create instances with specific field values
- ``reset(confirm=False)`` - Safely delete all records from model table with confirmation requirement

**Performance Improvements:**
- Bulk insert operations for large data sets
- Configurable batch sizes for optimal memory usage
- Intelligent batching that automatically splits large operations
- Lazy relationship loading for better performance

**Enhanced Error Handling:**
- New ``UniquenessError`` exception for unique constraint violations
- Detailed logging with configurable log levels
- Automatic transaction rollback on errors
- Specific handling for ``IntegrityError`` with intelligent error messages
- Better error context and stack traces

**Context Manager Support:**
- ``with ModelFaker(model, session) as faker:`` syntax
- Automatic cleanup and rollback on exceptions
- Safe resource management

**Framework Integration Improvements:**
- Enhanced Flask-SQLAlchemy integration
- Better Django ORM support
- Improved Tornado SQLAlchemy integration
- Automatic session detection across frameworks

Changed
^^^^^^^

- Dropped support for Python 3.6
- **BREAKING**: Enhanced ``ModelFakerConfig`` with new parameters (backward compatible with defaults)
- **BREAKING**: ``create()`` method now uses bulk operations for amounts > bulk_size
- Improved JSON data structure generation with more realistic nested objects
- Enhanced relationship handling with better foreign key support
- Better handling of nullable fields and default values
- Improved primary key detection and auto-increment handling

Fixed
^^^^^

- Fixed issue with PostgreSQL UUID field handling
- Improved compatibility with different SQLAlchemy versions
- Better handling of enum fields with complex structures
- Fixed memory leaks in bulk operations
- Improved error handling for malformed JSON in doc strings


[0.0.1] - 2025-03-01
--------------------

Added
^^^^^

- Updated test coverage.
- Allowed different types of primary keys than integer.
- Possibility to pass a custom faker instance to the ``ModelFaker``.
- ``ModelFakerConfig`` to define custom configurations.


[0.0.0] - 2025-02-02
--------------------

Added
^^^^^

Initial implementation.
