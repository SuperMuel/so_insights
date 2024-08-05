from datetime import date, datetime
from math import floor
from typing import Dict, Iterator, Tuple, overload
from src.models import Article
from pydantic import HttpUrl


class SetOfUniqueArticles:
    """
    A class designed to reduce the amount of duplicated or similar articles passed to LLMs.

    Articles are considered the same if any of the following conditions are met:
    - They have the same ID
    - They have the same URL
    - They have the same title (case insensitive, ignoring leading/trailing whitespaces)
      AND the same date (ignoring the time part if it exists)

    If articles have the same title and date but different bodies, the article with the longer body is kept.
    """

    def __init__(self, input_data: Article | list[Article] | None = None):
        self.articles_by_id: Dict[str, Article] = {}
        self.articles_by_url: Dict[HttpUrl, Article] = {}
        self.articles_by_title_date: Dict[Tuple[str, date], Article] = {}

        if not input_data:
            return

        if isinstance(input_data, Article):
            input_data = [input_data]

        for article in input_data:
            self.add_article(article)

    def _normalize_string(self, s: str) -> str:
        """
        Normalize a string by trimming whitespace and converting to lowercase.
        """
        return s.strip().lower()

    def _normalize_date(self, d: datetime) -> date:
        """
        Normalize a date or datetime by extracting the date part.
        """
        if isinstance(d, datetime):
            return d.date()
        return d

    def _generate_title_date_key(self, article: Article) -> Tuple[str, date]:
        """
        Generate a key for an article based on its normalized title and date.
        """
        normalized_title = self._normalize_string(article.title)
        normalized_date = self._normalize_date(article.date)
        return (normalized_title, normalized_date)

    def add_article(self, article: Article):
        """
        Add an article to the set of unique articles.

        Args:
            article (Article): The article to add.
        """
        # Check for ID uniqueness
        if article.id and str(article.id) in self.articles_by_id:
            return

        # Check for URL uniqueness
        if article.url in self.articles_by_url:
            return

        title_date_key = self._generate_title_date_key(article)
        normalized_body = self._normalize_string(article.body)

        if title_date_key not in self.articles_by_title_date:
            self._add_article_to_all_dicts(article, title_date_key)
            return

        existing_article = self.articles_by_title_date[title_date_key]
        existing_body = self._normalize_string(existing_article.body)

        if (
            normalized_body != existing_body
            and normalized_body.startswith(
                existing_body[
                    : floor(
                        len(existing_body) * 0.9
                    )  # fix if for instance, the shorter existing body ends with an extra dot
                ]
            )
        ):
            self._remove_article_from_all_dicts(existing_article)
            self._add_article_to_all_dicts(article, title_date_key)

    def _add_article_to_all_dicts(
        self, article: Article, title_date_key: Tuple[str, date]
    ):
        """
        Add an article to all internal dictionaries.
        """
        if article.id:
            self.articles_by_id[str(article.id)] = article
        self.articles_by_url[article.url] = article
        self.articles_by_title_date[title_date_key] = article

    def _remove_article_from_all_dicts(self, article: Article):
        """
        Remove an article from all internal dictionaries.
        """
        if article.id:
            self.articles_by_id.pop(str(article.id), None)
        self.articles_by_url.pop(article.url, None)
        title_date_key = self._generate_title_date_key(article)
        self.articles_by_title_date.pop(title_date_key, None)

    def get_articles(self) -> list[Article]:
        """
        Get the list of unique articles.
        """
        return list(self.articles_by_title_date.values())

    def __iter__(self) -> Iterator[Article]:
        """
        Return an iterator over the unique articles.
        """
        return iter(self.get_articles())

    def __repr__(self) -> str:
        """
        Return a string representation of the set of unique articles.
        """
        articles = [article.__repr__() for article in self.get_articles()]
        class_name = self.__class__.__name__
        return f"{class_name}([{',\n    '.join(articles)}])"

    def __bool__(self) -> bool:
        """
        Return True if the set of unique articles is not empty, False otherwise.

        Returns:
            bool: True if the set of unique articles is not empty, False otherwise.
        """
        return bool(self.articles_by_title_date)

    def limit(self, n: int | None) -> "SetOfUniqueArticles":
        """
        Limit the number of articles to be returned. Note: subsequent calls to `add_article` will not be limited.

        Args:
            n (int | None): The maximum number of articles to return. If None, the limit has no effect.

        Returns:
            SetOfUniqueArticles: A new SetOfUniqueArticles instance with the limited number of articles.
        """
        articles = self.get_articles() if n is None else self.get_articles()[:n]

        return SetOfUniqueArticles(list(articles))

    def __len__(self) -> int:
        return len(self.articles_by_title_date)

    @overload
    def __getitem__(self, key: int) -> Article: ...

    @overload
    def __getitem__(self, key: slice) -> list[Article]: ...

    def __getitem__(self, key: int | slice) -> Article | list[Article]:
        """
        Enable indexing and slicing of the SetOfUniqueArticles.

        Args:
            key (Union[int, slice]): The index or slice to retrieve.

        Returns:
            Union[Article, List[Article]]: An Article for integer index, or a list of Articles for a slice.

        Raises:
            IndexError: If the index is out of range.
        """
        articles = self.get_articles()

        if isinstance(key, int):
            try:
                return articles[key]
            except IndexError:
                raise IndexError("SetOfUniqueArticles index out of range")

        elif isinstance(key, slice):
            return articles[key]

        else:
            raise TypeError("Invalid argument type")
