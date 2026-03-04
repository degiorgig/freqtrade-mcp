"""Documentation reader for freqtrade markdown docs.

Provides read-only access to the freqtrade documentation files.
Loads and caches markdown content with TTL-based expiration.
"""

import logging
import os
from pathlib import Path

from freqtrade_mcp.cache import ttl_cache
from freqtrade_mcp.constants import (
    DOC_SEARCH_CONTEXT_LINES,
    ENV_DOCS_PATH,
    MAX_DOC_SEARCH_RESULTS,
)
from freqtrade_mcp.exceptions import DocTopicNotFoundError
from freqtrade_mcp.models import DocContent, DocSearchResult, DocTopic
from freqtrade_mcp.validators import (
    validate_doc_search_query,
    validate_doc_topic,
    validate_filter_string,
)

logger = logging.getLogger(__name__)

# Subdirectories to scan for markdown files
_SCAN_SUBDIRS: tuple[str, ...] = ("commands", "includes")


def _discover_docs_path() -> Path | None:
    """Discover the freqtrade documentation directory.

    Checks ``FREQTRADE_DOCS_PATH`` env var. If not set or invalid,
    returns None and logs a warning.

    Returns:
        Path to the docs directory, or None if not found.
    """
    env_path = os.environ.get(ENV_DOCS_PATH)
    if not env_path:
        logger.warning(
            "Freqtrade documentation not configured. Set %s to enable doc tools.",
            ENV_DOCS_PATH,
        )
        return None

    p = Path(env_path)
    if p.is_dir() and any(p.glob("*.md")):
        logger.info("Using docs path from %s: %s", ENV_DOCS_PATH, p)
        return p.resolve()

    logger.warning(
        "%s is set to '%s' but no markdown files found there.",
        ENV_DOCS_PATH,
        env_path,
    )
    return None


def _extract_title(content: str, filename: str) -> str:
    """Extract the H1 title from markdown content.

    Args:
        content: Full markdown content.
        filename: Filename for fallback title.

    Returns:
        The document title.
    """
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("##"):
            return stripped[2:].strip()
    # Fallback: humanize filename
    stem = filename.rsplit(".", maxsplit=1)[0]
    return stem.replace("-", " ").replace("_", " ").title()


def _is_safe_path(filepath: Path, docs_root: Path) -> bool:
    """Verify that a file path is safely under the docs root.

    Args:
        filepath: The resolved file path to check.
        docs_root: The resolved docs root directory.

    Returns:
        True if the path is safely under docs_root.
    """
    try:
        filepath.resolve().relative_to(docs_root.resolve())
    except ValueError:
        return False
    return True


def _scan_directory(
    directory: Path,
    docs_root: Path,
    prefix: str = "",
) -> dict[str, tuple[str, str, int]]:
    """Scan a directory for markdown files and build index entries.

    Args:
        directory: Directory to scan.
        docs_root: Root docs directory for safety checks.
        prefix: Topic prefix (e.g., "commands/" for subdirectories).

    Returns:
        Dictionary mapping topic names to (title, content, size) tuples.
    """
    index: dict[str, tuple[str, str, int]] = {}

    if not directory.is_dir():
        return index

    for md_file in sorted(directory.glob("*.md")):
        if not md_file.is_file():
            continue
        if not _is_safe_path(md_file, docs_root):
            continue

        topic = f"{prefix}{md_file.stem}"
        try:
            content = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            logger.warning("Failed to read %s: %s", md_file, e)
            continue

        title = _extract_title(content, md_file.name)
        index[topic] = (title, content, md_file.stat().st_size)

    return index


@ttl_cache()
def _load_docs_index() -> dict[str, tuple[str, str, int]] | None:
    """Load and index all documentation files.

    Returns:
        Dictionary mapping topic names to (title, content, size_bytes) tuples,
        or None if docs are not available.
    """
    docs_path = _discover_docs_path()
    if docs_path is None:
        return None

    # Scan top-level .md files
    index = _scan_directory(docs_path, docs_path)

    # Scan known subdirectories
    for subdir in _SCAN_SUBDIRS:
        subdir_path = docs_path / subdir
        sub_index = _scan_directory(subdir_path, docs_path, prefix=f"{subdir}/")
        index.update(sub_index)

    logger.info("Loaded %d documentation topics", len(index))
    return index


# --- Public API ---


def list_docs(filter_str: str | None = None) -> list[DocTopic] | None:
    """List available documentation topics.

    Args:
        filter_str: Optional filter keyword.

    Returns:
        List of DocTopic summaries, or None if docs unavailable.
    """
    validated_filter: str | None = None
    if filter_str:
        validated_filter = validate_filter_string(filter_str, label="docs filter")

    index = _load_docs_index()
    if index is None:
        return None

    topics: list[DocTopic] = []
    for topic_name, (title, _content, size) in sorted(index.items()):
        if validated_filter:
            searchable = f"{topic_name} {title}".lower()
            if validated_filter not in searchable:
                continue

        topics.append(
            DocTopic(
                topic=topic_name,
                title=title,
                path=f"{topic_name}.md",
                size_bytes=size,
            )
        )

    return topics


def search_docs(
    query: str,
    max_results: int = 10,
) -> list[DocSearchResult] | None:
    """Full-text search across all documentation.

    Args:
        query: Search query text.
        max_results: Maximum results to return.

    Returns:
        List of search results with context snippets, or None if docs unavailable.
    """
    validated_query = validate_doc_search_query(query)
    max_results = min(max_results, MAX_DOC_SEARCH_RESULTS)

    index = _load_docs_index()
    if index is None:
        return None

    query_words = validated_query.lower().split()
    if not query_words:
        return []

    results: list[DocSearchResult] = []

    for topic_name, (title, content, _size) in sorted(index.items()):
        lines = content.splitlines()
        content_lower = content.lower()

        # Quick reject: all query words must appear somewhere in the doc
        if not all(word in content_lower for word in query_words):
            continue

        # Find lines where at least one query word appears
        matching_lines: list[int] = []
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(word in line_lower for word in query_words):
                matching_lines.append(i)

        if not matching_lines:
            continue

        # Extract snippets with deduplication of overlapping context
        consumed: set[int] = set()
        for match_line in matching_lines:
            if match_line in consumed:
                continue

            start = max(0, match_line - DOC_SEARCH_CONTEXT_LINES)
            end = min(len(lines), match_line + DOC_SEARCH_CONTEXT_LINES + 1)
            snippet = "\n".join(lines[start:end])

            consumed.update(range(start, end))

            results.append(
                DocSearchResult(
                    topic=topic_name,
                    title=title,
                    line_number=match_line + 1,
                    snippet=snippet,
                )
            )

            if len(results) >= max_results:
                return results

    return results


def get_doc(topic: str) -> DocContent | None:
    """Get full content of a documentation page.

    Args:
        topic: Topic name to retrieve.

    Returns:
        DocContent with full markdown, or None if docs unavailable.

    Raises:
        DocTopicNotFoundError: If the topic does not exist.
    """
    validated_topic = validate_doc_topic(topic)

    index = _load_docs_index()
    if index is None:
        return None

    entry = index.get(validated_topic)
    if entry is None:
        available = sorted(index.keys())
        suggestions = [t for t in available if validated_topic in t or t in validated_topic][:5]
        msg = f"Documentation topic '{validated_topic}' not found."
        if suggestions:
            msg += f" Did you mean: {', '.join(suggestions)}?"
        else:
            msg += " Use freqtrade_list_docs to see available topics."
        raise DocTopicNotFoundError(msg)

    title, content, size = entry
    return DocContent(
        topic=validated_topic,
        title=title,
        content=content,
        size_bytes=size,
    )
