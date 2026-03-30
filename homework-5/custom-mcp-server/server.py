from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("custom-lorem-reader")

BASE_DIR = Path(__file__).resolve().parent
LOREM_FILE = BASE_DIR / "lorem-ipsum.md"
DEFAULT_WORD_COUNT = 30


def _read_lorem_words(word_count: int = DEFAULT_WORD_COUNT) -> str:
    if word_count <= 0:
        raise ValueError("word_count must be a positive integer")

    text = LOREM_FILE.read_text(encoding="utf-8")
    words = text.split()
    return " ".join(words[:word_count])


@mcp.resource("resource://lorem-ipsum")
def lorem_default() -> str:
    return _read_lorem_words(DEFAULT_WORD_COUNT)


@mcp.resource("resource://lorem-ipsum/{word_count}")
def lorem_with_limit(word_count: int = DEFAULT_WORD_COUNT) -> str:
    return _read_lorem_words(word_count)


@mcp.tool()
def read(word_count: int = DEFAULT_WORD_COUNT) -> str:
    """Read lorem ipsum text with a configurable word limit."""
    return _read_lorem_words(word_count)


if __name__ == "__main__":
    mcp.run()

