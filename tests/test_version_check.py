"""Tests for freqtrade version checking."""

from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

import pytest

from freqtrade_mcp._version_check import _parse_version_tuple, check_freqtrade_version
from freqtrade_mcp.exceptions import VersionError


class TestParseVersionTuple:
    """Tests for _parse_version_tuple."""

    def test_simple_version(self) -> None:
        """Simple version strings should parse correctly."""
        assert _parse_version_tuple("2026.2") == (2026, 2)

    def test_three_part_version(self) -> None:
        """Three-part version strings should parse correctly."""
        assert _parse_version_tuple("2026.2.1") == (2026, 2, 1)

    def test_prerelease_version(self) -> None:
        """Pre-release suffixes should be stripped."""
        assert _parse_version_tuple("2026.2rc1") == (2026, 2)

    def test_dev_version(self) -> None:
        """Dev version suffixes should be handled."""
        assert _parse_version_tuple("2026.3dev1") == (2026, 3)


class TestCheckFreqtradeVersion:
    """Tests for check_freqtrade_version."""

    def test_not_installed(self) -> None:
        """Should raise VersionError when freqtrade is not installed."""
        with (
            patch(
                "freqtrade_mcp._version_check.version",
                side_effect=PackageNotFoundError("freqtrade"),
            ),
            pytest.raises(VersionError, match="not installed"),
        ):
            check_freqtrade_version()

    def test_version_too_old(self) -> None:
        """Should raise VersionError when version is below minimum."""
        with (
            patch("freqtrade_mcp._version_check.version", return_value="2025.1"),
            pytest.raises(VersionError, match="requires >="),
        ):
            check_freqtrade_version()

    def test_exact_minimum_version(self) -> None:
        """Should accept the exact minimum version."""
        with patch("freqtrade_mcp._version_check.version", return_value="2026.2"):
            result = check_freqtrade_version()
            assert result == "2026.2"

    def test_newer_version(self) -> None:
        """Should accept newer versions."""
        with patch("freqtrade_mcp._version_check.version", return_value="2026.5"):
            result = check_freqtrade_version()
            assert result == "2026.5"
