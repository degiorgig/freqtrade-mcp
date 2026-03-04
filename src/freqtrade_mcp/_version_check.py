"""Startup validation of the installed freqtrade version."""

import logging
from importlib.metadata import PackageNotFoundError, version

from freqtrade_mcp.constants import MIN_FREQTRADE_VERSION
from freqtrade_mcp.exceptions import VersionError

logger = logging.getLogger(__name__)


def _parse_version_tuple(version_str: str) -> tuple[int, ...]:
    """Parse a version string into a comparable tuple of integers.

    Args:
        version_str: Version string like "2026.2" or "2026.2.1".

    Returns:
        Tuple of integers for comparison.
    """
    parts: list[int] = []
    for part in version_str.split("."):
        # Strip any pre-release suffixes (e.g., "2026.2rc1" -> "2026")
        numeric = ""
        for char in part:
            if char.isdigit():
                numeric += char
            else:
                break
        if numeric:
            parts.append(int(numeric))
    return tuple(parts)


def check_freqtrade_version() -> str:
    """Validate that freqtrade is installed and meets the minimum version.

    Returns:
        The installed freqtrade version string.

    Raises:
        VersionError: If freqtrade is not installed or version is too old.
    """
    try:
        installed_version = version("freqtrade")
    except PackageNotFoundError as exc:
        msg = (
            "freqtrade is not installed. "
            f"Please install freqtrade >= {MIN_FREQTRADE_VERSION} to use freqtrade-mcp."
        )
        raise VersionError(msg) from exc

    installed_tuple = _parse_version_tuple(installed_version)
    required_tuple = _parse_version_tuple(MIN_FREQTRADE_VERSION)

    if installed_tuple < required_tuple:
        msg = (
            f"freqtrade {installed_version} is installed, "
            f"but freqtrade-mcp requires >= {MIN_FREQTRADE_VERSION}. "
            "Please upgrade freqtrade."
        )
        raise VersionError(msg)

    logger.info("freqtrade %s detected (minimum: %s)", installed_version, MIN_FREQTRADE_VERSION)
    return installed_version
