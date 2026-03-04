"""MCP server integration tests."""

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from freqtrade_mcp.server import (
    freqtrade_get_callback_info,
    freqtrade_get_class_info,
    freqtrade_get_config_schema,
    freqtrade_get_dataframe_columns,
    freqtrade_get_doc,
    freqtrade_get_enum_values,
    freqtrade_get_method_signature,
    freqtrade_get_version_info,
    freqtrade_list_docs,
    freqtrade_list_enums,
    freqtrade_list_strategy_methods,
    freqtrade_search_codebase,
    freqtrade_search_docs,
)


class TestListStrategyMethodsTool:
    """Tests for freqtrade_list_strategy_methods tool."""

    def test_returns_list_of_dicts(self, fake_freqtrade_modules: Any) -> None:
        """Should return list of dictionaries."""
        result = freqtrade_list_strategy_methods()
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], dict)
        assert "name" in result[0]
        assert "brief" in result[0]
        assert "is_callback" in result[0]

    def test_with_filter(self, fake_freqtrade_modules: Any) -> None:
        """Should accept filter parameter."""
        result = freqtrade_list_strategy_methods(filter="entry")
        assert isinstance(result, list)
        names = [m["name"] for m in result]
        assert "populate_entry_trend" in names

    def test_with_none_filter(self, fake_freqtrade_modules: Any) -> None:
        """Should work with None filter."""
        result = freqtrade_list_strategy_methods(filter=None)
        assert isinstance(result, list)
        assert len(result) > 0


class TestGetMethodSignatureTool:
    """Tests for freqtrade_get_method_signature tool."""

    def test_returns_dict(self, fake_freqtrade_modules: Any) -> None:
        """Should return a dictionary with signature details."""
        result = freqtrade_get_method_signature(method_name="populate_indicators")
        assert isinstance(result, dict)
        assert result["name"] == "populate_indicators"
        assert "parameters" in result
        assert "return_type" in result
        assert "docstring" in result

    def test_parameters_structure(self, fake_freqtrade_modules: Any) -> None:
        """Parameters should have proper structure."""
        result = freqtrade_get_method_signature(method_name="populate_indicators")
        params = result["parameters"]
        assert isinstance(params, list)
        for p in params:
            assert "name" in p
            assert "annotation" in p
            assert "kind" in p


class TestGetClassInfoTool:
    """Tests for freqtrade_get_class_info tool."""

    def test_returns_dict(self, fake_freqtrade_modules: Any) -> None:
        """Should return a dictionary with class info."""
        result = freqtrade_get_class_info(class_path="freqtrade.strategy.interface.IStrategy")
        assert isinstance(result, dict)
        assert result["name"] == "IStrategy"
        assert "method_resolution_order" in result
        assert "public_methods" in result
        assert "class_attributes" in result


class TestListEnumsTool:
    """Tests for freqtrade_list_enums tool."""

    def test_returns_list_of_dicts(self, fake_freqtrade_modules: Any) -> None:
        """Should return list of enum dictionaries."""
        result = freqtrade_list_enums()
        assert isinstance(result, list)
        assert len(result) >= 2
        for item in result:
            assert "name" in item
            assert "module" in item
            assert "member_count" in item


class TestGetEnumValuesTool:
    """Tests for freqtrade_get_enum_values tool."""

    def test_returns_dict(self, fake_freqtrade_modules: Any) -> None:
        """Should return dict with enum members."""
        result = freqtrade_get_enum_values(enum_path="freqtrade.enums.SignalDirection")
        assert isinstance(result, dict)
        assert result["name"] == "SignalDirection"
        assert len(result["members"]) == 2


class TestSearchCodebaseTool:
    """Tests for freqtrade_search_codebase tool."""

    def test_returns_list(self, fake_freqtrade_modules: Any) -> None:
        """Should return list of matches."""
        result = freqtrade_search_codebase(query="Signal")
        assert isinstance(result, list)


class TestGetCallbackInfoTool:
    """Tests for freqtrade_get_callback_info tool."""

    def test_returns_dict(self, fake_freqtrade_modules: Any) -> None:
        """Should return callback info dict."""
        result = freqtrade_get_callback_info(callback_name="custom_stoploss")
        assert isinstance(result, dict)
        assert result["name"] == "custom_stoploss"
        assert "signature" in result
        assert "parameters" in result
        assert "docstring" in result


class TestGetConfigSchemaTool:
    """Tests for freqtrade_get_config_schema tool."""

    def test_returns_list(self, fake_freqtrade_modules: Any) -> None:
        """Should return list of config keys."""
        result = freqtrade_get_config_schema()
        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert "key" in item
            assert "description" in item

    def test_with_section_filter(self, fake_freqtrade_modules: Any) -> None:
        """Should accept section filter."""
        result = freqtrade_get_config_schema(section="exchange")
        assert isinstance(result, list)


class TestGetDataframeColumnsTool:
    """Tests for freqtrade_get_dataframe_columns tool."""

    def test_returns_list(self) -> None:
        """Should return list of column entries."""
        result = freqtrade_get_dataframe_columns()
        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert "name" in item
            assert "description" in item
            assert "context" in item

    def test_with_context_filter(self) -> None:
        """Should accept context filter."""
        result = freqtrade_get_dataframe_columns(context="ohlcv")
        names = [c["name"] for c in result]
        assert "open" in names
        assert "close" in names


class TestGetVersionInfoTool:
    """Tests for freqtrade_get_version_info tool."""

    def test_returns_version_dict(self) -> None:
        """Should return version info dictionary."""
        with patch("freqtrade_mcp.server.check_freqtrade_version", return_value="2026.3"):
            result = freqtrade_get_version_info()
            assert isinstance(result, dict)
            assert "mcp_server_version" in result
            assert "freqtrade_version" in result
            assert "python_version" in result
            assert result["freqtrade_version"] == "2026.3"


class TestListDocsTool:
    """Tests for freqtrade_list_docs tool."""

    def test_returns_list_when_available(
        self, monkeypatch: pytest.MonkeyPatch, fake_docs_dir: Path
    ) -> None:
        monkeypatch.setenv("FREQTRADE_DOCS_PATH", str(fake_docs_dir))
        result = freqtrade_list_docs()
        assert isinstance(result, list)
        assert len(result) == 5
        topics = [t["topic"] for t in result]
        assert "strategy-callbacks" in topics
        assert "commands/backtesting" in topics

    def test_returns_error_when_unavailable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("FREQTRADE_DOCS_PATH", raising=False)
        result = freqtrade_list_docs()
        assert isinstance(result, dict)
        assert "error" in result

    def test_with_filter(self, monkeypatch: pytest.MonkeyPatch, fake_docs_dir: Path) -> None:
        monkeypatch.setenv("FREQTRADE_DOCS_PATH", str(fake_docs_dir))
        result = freqtrade_list_docs(filter="strategy")
        assert isinstance(result, list)
        assert len(result) >= 1


class TestSearchDocsTool:
    """Tests for freqtrade_search_docs tool."""

    def test_returns_list_when_available(
        self, monkeypatch: pytest.MonkeyPatch, fake_docs_dir: Path
    ) -> None:
        monkeypatch.setenv("FREQTRADE_DOCS_PATH", str(fake_docs_dir))
        result = freqtrade_search_docs(query="stoploss")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_returns_error_when_unavailable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("FREQTRADE_DOCS_PATH", raising=False)
        result = freqtrade_search_docs(query="anything")
        assert isinstance(result, dict)
        assert "error" in result

    def test_with_max_results(self, monkeypatch: pytest.MonkeyPatch, fake_docs_dir: Path) -> None:
        monkeypatch.setenv("FREQTRADE_DOCS_PATH", str(fake_docs_dir))
        result = freqtrade_search_docs(query="the", max_results=1)
        assert isinstance(result, list)
        assert len(result) <= 1


class TestGetDocTool:
    """Tests for freqtrade_get_doc tool."""

    def test_returns_dict_when_available(
        self, monkeypatch: pytest.MonkeyPatch, fake_docs_dir: Path
    ) -> None:
        monkeypatch.setenv("FREQTRADE_DOCS_PATH", str(fake_docs_dir))
        result = freqtrade_get_doc(topic="strategy-callbacks")
        assert isinstance(result, dict)
        assert result["topic"] == "strategy-callbacks"
        assert "content" in result

    def test_returns_error_when_unavailable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("FREQTRADE_DOCS_PATH", raising=False)
        result = freqtrade_get_doc(topic="strategy-callbacks")
        assert isinstance(result, dict)
        assert "error" in result

    def test_topic_not_found(self, monkeypatch: pytest.MonkeyPatch, fake_docs_dir: Path) -> None:
        monkeypatch.setenv("FREQTRADE_DOCS_PATH", str(fake_docs_dir))
        from freqtrade_mcp.exceptions import DocTopicNotFoundError

        with pytest.raises(DocTopicNotFoundError):
            freqtrade_get_doc(topic="nonexistent-topic")
