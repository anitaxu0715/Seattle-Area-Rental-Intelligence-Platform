"""Tests for database utilities."""

import pytest

from src.utils.database import validate_table_name


def test_valid_table_names():
    assert validate_table_name("raw_building_permits") == "raw_building_permits"
    assert validate_table_name("raw_rental_registration") == "raw_rental_registration"
    assert validate_table_name("raw_code_violations") == "raw_code_violations"


def test_invalid_table_names():
    with pytest.raises(ValueError):
        validate_table_name("DROP TABLE users;")

    with pytest.raises(ValueError):
        validate_table_name("raw-table")

    with pytest.raises(ValueError):
        validate_table_name("123_starts_with_number")

    with pytest.raises(ValueError):
        validate_table_name("")
