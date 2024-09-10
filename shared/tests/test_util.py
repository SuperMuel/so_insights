from shared.util import validate_url


def test_validate_url_with_valid_url():
    assert validate_url("http://example.com") == "http://example.com"
    assert validate_url("https://example.com") == "https://example.com"
    assert (
        validate_url("http://example.com/image.jpg") == "http://example.com/image.jpg"
    )


def test_validate_url_with_invalid_url():
    assert validate_url("example.com") is None
    assert validate_url("http://") is None
    assert validate_url("https://") is None


def test_validate_url_with_non_string_input():
    assert validate_url(12345) is None
    assert validate_url(None) is None
    assert validate_url([]) is None
    assert validate_url({}) is None


def test_validate_url_with_empty_string():
    assert validate_url("") is None
