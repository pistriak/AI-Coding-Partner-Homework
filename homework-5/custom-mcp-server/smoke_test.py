from server import DEFAULT_WORD_COUNT, _read_lorem_words


def assert_word_count(value: str, expected_count: int) -> None:
    actual_count = len(value.split())
    if actual_count != expected_count:
        raise AssertionError(f"Expected {expected_count} words, got {actual_count}")


def main() -> None:
    assert_word_count(_read_lorem_words(), DEFAULT_WORD_COUNT)
    assert_word_count(_read_lorem_words(5), 5)

    try:
        _read_lorem_words(0)
    except ValueError:
        pass
    else:
        raise AssertionError("word_count=0 should raise ValueError")

    print("Smoke tests passed.")


if __name__ == "__main__":
    main()

