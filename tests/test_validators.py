"""Tests for input validation."""

import re

import pytest

from freqtrade_mcp.exceptions import ValidationError
from freqtrade_mcp.validators import (
    validate_class_path,
    validate_filter_string,
    validate_identifier,
    validate_module_path,
    validate_search_pattern,
)


class TestValidateIdentifier:
    """Tests for validate_identifier."""

    def test_valid_identifiers(self) -> None:
        """Valid Python identifiers should pass."""
        assert validate_identifier("foo") == "foo"
        assert validate_identifier("Foo_Bar") == "Foo_Bar"
        assert validate_identifier("_private") == "_private"
        assert validate_identifier("CamelCase123") == "CamelCase123"

    def test_empty_string(self) -> None:
        """Empty string should fail."""
        with pytest.raises(ValidationError, match="must be 1-"):
            validate_identifier("")

    def test_too_long(self) -> None:
        """Overly long string should fail."""
        with pytest.raises(ValidationError, match="must be 1-"):
            validate_identifier("a" * 300)

    def test_invalid_characters(self) -> None:
        """Strings with invalid characters should fail."""
        with pytest.raises(ValidationError, match="not a valid Python identifier"):
            validate_identifier("foo.bar")
        with pytest.raises(ValidationError, match="not a valid Python identifier"):
            validate_identifier("foo bar")
        with pytest.raises(ValidationError, match="not a valid Python identifier"):
            validate_identifier("123abc")

    def test_shell_metacharacters(self) -> None:
        """Shell metacharacters should fail."""
        for bad in ["foo;rm", "$(cmd)", "foo|bar", "foo&bar", "foo`cmd`"]:
            with pytest.raises(ValidationError):
                validate_identifier(bad)

    def test_path_traversal(self) -> None:
        """Path traversal attempts should fail."""
        with pytest.raises(ValidationError):
            validate_identifier("../etc/passwd")
        with pytest.raises(ValidationError):
            validate_identifier("foo/bar")


class TestValidateModulePath:
    """Tests for validate_module_path."""

    def test_valid_paths(self) -> None:
        """Valid freqtrade module paths should pass."""
        assert validate_module_path("freqtrade.strategy") == "freqtrade.strategy"
        assert (
            validate_module_path("freqtrade.strategy.interface") == "freqtrade.strategy.interface"
        )
        assert validate_module_path("freqtrade.enums") == "freqtrade.enums"

    def test_must_start_with_freqtrade(self) -> None:
        """Paths not starting with freqtrade. should fail."""
        with pytest.raises(ValidationError, match=r"must start with 'freqtrade\.'"):
            validate_module_path("os.path")
        with pytest.raises(ValidationError, match=r"must start with 'freqtrade\.'"):
            validate_module_path("sys")

    def test_freqtrade_alone_fails(self) -> None:
        """Just 'freqtrade' without submodule should fail."""
        with pytest.raises(ValidationError, match=r"must start with 'freqtrade\.'"):
            validate_module_path("freqtrade")

    def test_empty_string(self) -> None:
        """Empty string should fail."""
        with pytest.raises(ValidationError, match="must be 1-"):
            validate_module_path("")

    def test_invalid_characters(self) -> None:
        """Paths with invalid chars should fail."""
        with pytest.raises(ValidationError, match="contains invalid characters"):
            validate_module_path("freqtrade.strategy-interface")
        with pytest.raises(ValidationError, match="contains invalid characters"):
            validate_module_path("freqtrade.strategy interface")

    def test_path_traversal(self) -> None:
        """Path traversal in module paths should fail."""
        with pytest.raises(ValidationError):
            validate_module_path("freqtrade.../../etc")


class TestValidateClassPath:
    """Tests for validate_class_path."""

    def test_valid_class_path(self) -> None:
        """Valid class paths should return (module, class) tuple."""
        module, cls = validate_class_path("freqtrade.strategy.interface.IStrategy")
        assert module == "freqtrade.strategy.interface"
        assert cls == "IStrategy"

    def test_valid_enum_path(self) -> None:
        """Valid enum paths should work."""
        module, cls = validate_class_path("freqtrade.enums.SignalDirection")
        assert module == "freqtrade.enums"
        assert cls == "SignalDirection"

    def test_no_dot(self) -> None:
        """Path without dots should fail."""
        with pytest.raises(ValidationError, match="must be a dotted path"):
            validate_class_path("IStrategy")

    def test_non_freqtrade(self) -> None:
        """Non-freqtrade paths should fail."""
        with pytest.raises(ValidationError, match=r"must start with 'freqtrade\.'"):
            validate_class_path("os.path.Path")

    def test_empty(self) -> None:
        """Empty path should fail."""
        with pytest.raises(ValidationError, match="must be 1-"):
            validate_class_path("")


class TestValidateSearchPattern:
    """Tests for validate_search_pattern."""

    def test_valid_patterns(self) -> None:
        """Safe regex patterns should compile."""
        pat = validate_search_pattern("IStrategy")
        assert isinstance(pat, re.Pattern)
        assert pat.search("IStrategy") is not None

    def test_case_insensitive(self) -> None:
        """Patterns should be case-insensitive."""
        pat = validate_search_pattern("istrategy")
        assert pat.search("IStrategy") is not None

    def test_wildcard_pattern(self) -> None:
        """Wildcards should work."""
        pat = validate_search_pattern("custom_.*")
        assert pat.search("custom_stoploss") is not None

    def test_empty_pattern(self) -> None:
        """Empty pattern should fail."""
        with pytest.raises(ValidationError, match="must be 1-"):
            validate_search_pattern("")

    def test_too_long(self) -> None:
        """Overly long pattern should fail."""
        with pytest.raises(ValidationError, match="must be 1-"):
            validate_search_pattern("a" * 300)


class TestValidateFilterString:
    """Tests for validate_filter_string."""

    def test_valid_filters(self) -> None:
        """Valid filter strings should pass and be lowercased."""
        assert validate_filter_string("entry") == "entry"
        assert validate_filter_string("EXIT") == "exit"
        assert validate_filter_string("custom_stoploss") == "custom_stoploss"

    def test_empty_filter(self) -> None:
        """Empty filter should fail."""
        with pytest.raises(ValidationError, match="must be 1-"):
            validate_filter_string("")

    def test_invalid_characters(self) -> None:
        """Filters with special chars should fail."""
        with pytest.raises(ValidationError, match="contains invalid characters"):
            validate_filter_string("foo.bar")
        with pytest.raises(ValidationError, match="contains invalid characters"):
            validate_filter_string("foo bar")
