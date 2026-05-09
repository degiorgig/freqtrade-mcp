# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-05-09

### Added

- 3 new documentation tools for accessing freqtrade markdown docs:
  - `freqtrade_list_docs` — list available documentation topics with optional filter
  - `freqtrade_search_docs` — full-text search across all docs with AND semantics
  - `freqtrade_get_doc` — read a specific documentation page by topic name
- `FREQTRADE_DOCS_PATH` environment variable to configure docs directory
- Graceful degradation when docs are not available (server continues, tools return guidance)
- TTL-cached documentation index with automatic refresh
- Input validation for doc topics (path traversal prevention) and search queries
- `DocTopicNotFoundError` with close-match suggestions
- 47 new tests for documentation functionality

### Changed

- Clarified the intended MCP usage philosophy: read-only reference layer, public API first, and no reliance on undocumented Freqtrade internals in generated strategy code.

## [0.1.0] - 2026-03-03

### Added

- Initial release of freqtrade-mcp
- 10 read-only MCP tools for Freqtrade codebase introspection:
  - `freqtrade_list_strategy_methods` — list overridable IStrategy methods
  - `freqtrade_get_method_signature` — get full method signatures
  - `freqtrade_get_class_info` — inspect freqtrade classes
  - `freqtrade_list_enums` — list trading-related enums
  - `freqtrade_get_enum_values` — get enum member values
  - `freqtrade_search_codebase` — search symbols by pattern
  - `freqtrade_get_callback_info` — get strategy callback details
  - `freqtrade_get_config_schema` — browse configuration keys
  - `freqtrade_get_dataframe_columns` — list DataFrame columns
  - `freqtrade_get_version_info` — version information
- Input validation with regex whitelists
- TTL-based caching for introspection results
- Freqtrade version validation at startup
- Structured JSON logging to stderr
- Comprehensive test suite
- CI/CD with GitHub Actions
- Security documentation with MCP threat model

[Unreleased]: https://github.com/yalcin/freqtrade-mcp/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/yalcin/freqtrade-mcp/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/yalcin/freqtrade-mcp/releases/tag/v0.1.0
