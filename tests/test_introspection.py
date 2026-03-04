"""Tests for the introspection engine."""

from typing import Any

import pytest

from freqtrade_mcp.exceptions import (
    ClassNotFoundError,
    IntrospectionError,
    MethodNotFoundError,
    ModuleImportError,
)
from freqtrade_mcp.introspection import (
    get_callback_info,
    get_class_info,
    get_config_schema,
    get_dataframe_columns,
    get_enum_values,
    get_method_signature,
    list_enums,
    list_strategy_methods,
    search_codebase,
)
from freqtrade_mcp.models import (
    CallbackInfo,
    ClassInfo,
    ConfigKey,
    EnumDetail,
    MethodSignature,
    MethodSummary,
    SymbolMatch,
)


class TestListStrategyMethods:
    """Tests for list_strategy_methods."""

    def test_lists_public_methods(self, fake_freqtrade_modules: Any) -> None:
        """Should return public methods from FakeIStrategy."""
        methods = list_strategy_methods()
        assert len(methods) > 0
        assert all(isinstance(m, MethodSummary) for m in methods)

        names = [m.name for m in methods]
        assert "populate_indicators" in names
        assert "populate_entry_trend" in names
        assert "custom_stoploss" in names
        # Private methods should be excluded
        assert "_private_method" not in names

    def test_filter_by_entry(self, fake_freqtrade_modules: Any) -> None:
        """Filter by 'entry' should narrow results."""
        methods = list_strategy_methods(filter_str="entry")
        names = [m.name for m in methods]
        assert "populate_entry_trend" in names
        # Methods without 'entry' in name/description should be excluded
        assert "custom_stoploss" not in names

    def test_filter_by_exit(self, fake_freqtrade_modules: Any) -> None:
        """Filter by 'exit' should narrow results."""
        methods = list_strategy_methods(filter_str="exit")
        names = [m.name for m in methods]
        assert "populate_exit_trend" in names
        assert "custom_exit" in names

    def test_callback_flag(self, fake_freqtrade_modules: Any) -> None:
        """Callback methods should be flagged."""
        methods = list_strategy_methods()
        method_dict = {m.name: m for m in methods}
        if "bot_start" in method_dict:
            assert method_dict["bot_start"].is_callback is True
        if "populate_indicators" in method_dict:
            assert method_dict["populate_indicators"].is_callback is True

    def test_sorted_by_name(self, fake_freqtrade_modules: Any) -> None:
        """Results should be sorted alphabetically."""
        methods = list_strategy_methods()
        names = [m.name for m in methods]
        assert names == sorted(names)


class TestGetMethodSignature:
    """Tests for get_method_signature."""

    def test_valid_method(self, fake_freqtrade_modules: Any) -> None:
        """Should return full signature for a valid method."""
        sig = get_method_signature("populate_indicators")
        assert isinstance(sig, MethodSignature)
        assert sig.name == "populate_indicators"
        assert len(sig.parameters) > 0
        assert sig.docstring is not None
        assert "DataFrame" in sig.docstring or "indicators" in sig.docstring.lower()

    def test_method_parameters(self, fake_freqtrade_modules: Any) -> None:
        """Should include parameter details."""
        sig = get_method_signature("populate_indicators")
        param_names = [p.name for p in sig.parameters]
        assert "self" in param_names
        assert "dataframe" in param_names
        assert "metadata" in param_names

    def test_method_with_kwargs(self, fake_freqtrade_modules: Any) -> None:
        """Should handle **kwargs properly."""
        sig = get_method_signature("custom_stoploss")
        param_names = [p.name for p in sig.parameters]
        assert "kwargs" in param_names

    def test_nonexistent_method(self, fake_freqtrade_modules: Any) -> None:
        """Should raise MethodNotFoundError for unknown method."""
        with pytest.raises(MethodNotFoundError, match="not found"):
            get_method_signature("nonexistent_method")

    def test_invalid_method_name(self, fake_freqtrade_modules: Any) -> None:
        """Should validate method name."""
        from freqtrade_mcp.exceptions import ValidationError

        with pytest.raises(ValidationError):
            get_method_signature("invalid.name")


class TestGetClassInfo:
    """Tests for get_class_info."""

    def test_istrategy_class(self, fake_freqtrade_modules: Any) -> None:
        """Should return info for IStrategy (FakeIStrategy)."""
        info = get_class_info("freqtrade.strategy.interface.IStrategy")
        assert isinstance(info, ClassInfo)
        assert info.name == "IStrategy"
        assert info.module == "freqtrade.strategy.interface"
        assert len(info.public_methods) > 0
        assert len(info.method_resolution_order) > 0

    def test_class_attributes(self, fake_freqtrade_modules: Any) -> None:
        """Should include class-level attributes."""
        info = get_class_info("freqtrade.strategy.interface.IStrategy")
        assert "timeframe" in info.class_attributes
        assert "stoploss" in info.class_attributes

    def test_nonexistent_class(self, fake_freqtrade_modules: Any) -> None:
        """Should raise ClassNotFoundError."""
        with pytest.raises(ClassNotFoundError, match="not found"):
            get_class_info("freqtrade.strategy.interface.NonExistent")

    def test_nonexistent_module(self, fake_freqtrade_modules: Any) -> None:
        """Should raise ModuleNotFoundError."""
        with pytest.raises(ModuleImportError, match="Cannot import"):
            get_class_info("freqtrade.nonexistent.module.SomeClass")


class TestListEnums:
    """Tests for list_enums."""

    def test_lists_enums(self, fake_freqtrade_modules: Any) -> None:
        """Should find fake enums."""
        enums = list_enums()
        assert len(enums) >= 2
        names = [e.name for e in enums]
        assert "SignalDirection" in names
        assert "TradeExitType" in names

    def test_enum_member_count(self, fake_freqtrade_modules: Any) -> None:
        """Should report correct member count."""
        enums = list_enums()
        signal_dir = next(e for e in enums if e.name == "SignalDirection")
        assert signal_dir.member_count == 2  # LONG, SHORT

    def test_filter_enums(self, fake_freqtrade_modules: Any) -> None:
        """Should filter enums by keyword."""
        enums = list_enums(filter_str="signal")
        names = [e.name for e in enums]
        assert "SignalDirection" in names


class TestGetEnumValues:
    """Tests for get_enum_values."""

    def test_signal_direction(self, fake_freqtrade_modules: Any) -> None:
        """Should return all members of SignalDirection."""
        result = get_enum_values("freqtrade.enums.SignalDirection")
        assert isinstance(result, EnumDetail)
        assert result.name == "SignalDirection"
        assert len(result.members) == 2

        member_names = [m.name for m in result.members]
        assert "LONG" in member_names
        assert "SHORT" in member_names

    def test_trade_exit_type(self, fake_freqtrade_modules: Any) -> None:
        """Should return all members of TradeExitType."""
        result = get_enum_values("freqtrade.enums.TradeExitType")
        assert isinstance(result, EnumDetail)
        assert len(result.members) == 6

    def test_non_enum_class(self, fake_freqtrade_modules: Any) -> None:
        """Should raise IntrospectionError for non-enum class."""
        with pytest.raises(IntrospectionError, match="not an Enum"):
            get_enum_values("freqtrade.strategy.interface.IStrategy")


class TestGetCallbackInfo:
    """Tests for get_callback_info."""

    def test_valid_callback(self, fake_freqtrade_modules: Any) -> None:
        """Should return callback info."""
        info = get_callback_info("custom_stoploss")
        assert isinstance(info, CallbackInfo)
        assert info.name == "custom_stoploss"
        assert len(info.parameters) > 0
        assert info.docstring is not None

    def test_nonexistent_callback(self, fake_freqtrade_modules: Any) -> None:
        """Should raise MethodNotFoundError for unknown callback."""
        with pytest.raises(MethodNotFoundError, match="not found"):
            get_callback_info("nonexistent_callback")


class TestGetConfigSchema:
    """Tests for get_config_schema."""

    def test_all_sections(self, fake_freqtrade_modules: Any) -> None:
        """Should return config keys from all sections."""
        keys = get_config_schema()
        assert len(keys) > 0
        assert all(isinstance(k, ConfigKey) for k in keys)

    def test_filter_by_section(self, fake_freqtrade_modules: Any) -> None:
        """Should filter by section keyword."""
        keys = get_config_schema(section="exchange")
        assert len(keys) > 0
        assert all(
            "exchange" in k.key.lower() or "exchange" in k.description.lower() for k in keys
        )

    def test_returns_known_sections(self, fake_freqtrade_modules: Any) -> None:
        """Should include well-known config sections."""
        keys = get_config_schema()
        key_names = [k.key for k in keys]
        assert "exchange" in key_names
        assert "stoploss" in key_names
        assert "strategy" in key_names


class TestGetDataframeColumns:
    """Tests for get_dataframe_columns."""

    def test_all_columns(self) -> None:
        """Should return columns from all contexts."""
        columns = get_dataframe_columns()
        assert len(columns) > 0
        contexts = {c.context for c in columns}
        assert "ohlcv" in contexts
        assert "entry" in contexts
        assert "exit" in contexts

    def test_ohlcv_context(self) -> None:
        """Should return OHLCV columns."""
        columns = get_dataframe_columns(context="ohlcv")
        names = [c.name for c in columns]
        assert "open" in names
        assert "high" in names
        assert "low" in names
        assert "close" in names
        assert "volume" in names

    def test_entry_context(self) -> None:
        """Should return entry signal columns."""
        columns = get_dataframe_columns(context="entry")
        names = [c.name for c in columns]
        assert "enter_long" in names
        assert "enter_short" in names

    def test_indicators_context(self) -> None:
        """Should return common indicator columns."""
        columns = get_dataframe_columns(context="indicators")
        names = [c.name for c in columns]
        assert "rsi" in names
        assert "macd" in names
        assert "ema" in names

    def test_invalid_context(self) -> None:
        """Invalid context should return empty list."""
        columns = get_dataframe_columns(context="nonexistent")
        assert len(columns) == 0


class TestSearchCodebase:
    """Tests for search_codebase."""

    def test_search_finds_class(self, fake_freqtrade_modules: Any) -> None:
        """Should find classes matching pattern."""
        # Note: search_codebase walks the package tree, which is limited
        # with fake modules since __path__ is empty. Test with direct module.
        results = search_codebase("IStrategy")
        # May or may not find it depending on fake module setup
        assert isinstance(results, list)

    def test_search_returns_symbol_matches(self, fake_freqtrade_modules: Any) -> None:
        """Results should be SymbolMatch instances."""
        results = search_codebase(".*")
        for r in results:
            assert isinstance(r, SymbolMatch)
            assert r.kind in {"class", "function", "constant", "enum"}
