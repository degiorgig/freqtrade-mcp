"""Constants for freqtrade-mcp."""

import re
from typing import Final

# Minimum supported freqtrade version
MIN_FREQTRADE_VERSION: Final[str] = "2026.2"

# Default cache TTL in seconds (1 hour)
DEFAULT_CACHE_TTL: Final[int] = 3600

# Validation patterns
IDENTIFIER_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
MODULE_PATH_PATTERN: Final[re.Pattern[str]] = re.compile(r"^freqtrade(\.[A-Za-z_][A-Za-z0-9_]*)+$")
SAFE_REGEX_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9_.*+?^$|()\\[\]{}_ -]+$")

# Maximum length for input strings
MAX_INPUT_LENGTH: Final[int] = 256

# Freqtrade modules allowed for introspection
ALLOWED_TOP_LEVEL_MODULE: Final[str] = "freqtrade"

# IStrategy class path
ISTRATEGY_CLASS_PATH: Final[str] = "freqtrade.strategy.interface.IStrategy"

# Known strategy callback methods (informational, not exhaustive)
STRATEGY_CALLBACKS: Final[tuple[str, ...]] = (
    "bot_start",
    "bot_loop_start",
    "informative_pairs",
    "populate_indicators",
    "populate_entry_trend",
    "populate_exit_trend",
    "custom_stake_amount",
    "custom_exit",
    "custom_exit_price",
    "custom_entry_price",
    "custom_stoploss",
    "confirm_trade_entry",
    "confirm_trade_exit",
    "adjust_trade_position",
    "adjust_entry_price",
    "leverage",
    "order_filled",
    "protection_space",
)

# Known DataFrame column contexts
DATAFRAME_CONTEXTS: Final[dict[str, dict[str, str]]] = {
    "ohlcv": {
        "date": "Candle timestamp (datetime64)",
        "open": "Opening price (float64)",
        "high": "Highest price (float64)",
        "low": "Lowest price (float64)",
        "close": "Closing price (float64)",
        "volume": "Trading volume (float64)",
    },
    "entry": {
        "enter_long": "Long entry signal (int: 0 or 1)",
        "enter_short": "Short entry signal (int: 0 or 1)",
        "enter_tag": "Entry tag string for trade tracking (str, optional)",
    },
    "exit": {
        "exit_long": "Long exit signal (int: 0 or 1)",
        "exit_short": "Short exit signal (int: 0 or 1)",
        "exit_tag": "Exit tag string for trade tracking (str, optional)",
    },
}

# Known top-level config sections
CONFIG_SECTIONS: Final[tuple[str, ...]] = (
    "exchange",
    "pairlist",
    "stake_currency",
    "stake_amount",
    "dry_run",
    "trading_mode",
    "margin_mode",
    "strategy",
    "timeframe",
    "order_types",
    "order_time_in_force",
    "entry_pricing",
    "exit_pricing",
    "minimal_roi",
    "stoploss",
    "trailing_stop",
    "unfilledtimeout",
    "protections",
    "telegram",
    "api_server",
    "internals",
    "dataformat_ohlcv",
    "dataformat_trades",
)

# Documentation settings
ENV_DOCS_PATH: Final[str] = "FREQTRADE_DOCS_PATH"
DOC_TOPIC_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[a-zA-Z0-9][a-zA-Z0-9_-]*(/[a-zA-Z0-9][a-zA-Z0-9_-]*)*$"
)
DOC_SEARCH_CONTEXT_LINES: Final[int] = 3
MAX_DOC_SEARCH_RESULTS: Final[int] = 50
DOCS_UNAVAILABLE_MSG: Final[str] = (
    "Freqtrade documentation not available. "
    "Set FREQTRADE_DOCS_PATH environment variable to the freqtrade docs/ directory."
)

# Environment variable names
ENV_LOG_LEVEL: Final[str] = "FREQTRADE_MCP_LOG_LEVEL"

# Server metadata
SERVER_NAME: Final[str] = "freqtrade-mcp"
SERVER_DESCRIPTION: Final[str] = (
    "Read-only MCP server for Freqtrade codebase introspection. "
    "Helps LLMs write better Freqtrade strategy code by providing access to "
    "method signatures, docstrings, type hints, enums, and configuration schemas."
)
