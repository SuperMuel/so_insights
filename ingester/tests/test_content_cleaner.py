import pytest
from shared.content_fetching_models import ArticleContentCleanerOutput
from src.content_cleaner import ArticleContentCleaner


def test_parse_output_success():
    cleaner = ArticleContentCleaner()
    test_completion = """<title>Test Title</title>
<content>
This is the content
With multiple lines
And more content
</content>"""

    result = cleaner._parse_str_output(test_completion)

    assert isinstance(result, ArticleContentCleanerOutput)
    assert result.title == "Test Title"
    assert (
        result.cleaned_article_content
        == "This is the content\nWith multiple lines\nAnd more content"
    )
    assert result.error is None


def test_parse_output_error():
    cleaner = ArticleContentCleaner()
    test_completion = "<error>Invalid content format</error>"

    result = cleaner._parse_str_output(test_completion)

    assert isinstance(result, ArticleContentCleanerOutput)
    assert result.error == "Invalid content format"
    assert result.title is None
    assert result.cleaned_article_content is None


def test_parse_output_with_whitespace():
    cleaner = ArticleContentCleaner()
    test_completion = """
<title>
    Test Title
</title>
<content>
This is the content
With multiple lines
And more content
</content>
"""

    result = cleaner._parse_str_output(test_completion)

    assert isinstance(result, ArticleContentCleanerOutput)
    assert result.title == "Test Title"
    assert (
        result.cleaned_article_content
        == "This is the content\nWith multiple lines\nAnd more content"
    )
    assert result.error is None


def test_parse_output_invalid_format():
    cleaner = ArticleContentCleaner()
    test_completion = "Invalid format"

    with pytest.raises(ValueError):
        cleaner._parse_str_output(test_completion)


def test_parse_output_no_title():
    cleaner = ArticleContentCleaner()
    test_completion = "<content>This is the content</content>"

    with pytest.raises(ValueError):
        cleaner._parse_str_output(test_completion)


def test_parse_output_no_content():
    cleaner = ArticleContentCleaner()
    test_completion = "<title>Test Title</title>"

    with pytest.raises(ValueError):
        cleaner._parse_str_output(test_completion)
