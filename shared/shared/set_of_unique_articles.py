from datetime import date, datetime
from typing import Dict, Iterator, Tuple, overload
from shared.models import Article

from typing import List


class SetOfUniqueArticles:
    def __init__(self, input_data: Article | list[Article] | None = None):
        self.articles_by_id: Dict[str, Article] = {}
        self.articles_by_url: Dict[str, Article] = {}
        self.articles_by_title_date: Dict[Tuple[str, date], Article] = {}
        if input_data:
            articles = input_data if isinstance(input_data, list) else [input_data]
            for article in articles:
                self.add_article(article)

    def _get_article_id(self, article: Article) -> str | None:
        if hasattr(article, "id") and article.id:
            return str(article.id)
        if (
            hasattr(article, "field_id") and article.field_id
        ):  # To support the auto-generated Article class used in the frontend
            return str(article.field_id)
        return None

    def _normalize_string(self, s: str) -> str:
        """
        Normalize a string by trimming whitespace and converting to lowercase.
        """
        return s.strip().lower()

    def _normalize_date(self, d: datetime | date) -> date:
        """
        Normalize a date or datetime by extracting the date part.
        """
        return d.date() if isinstance(d, datetime) else d

    def _generate_title_date_key(self, article: Article) -> Tuple[str, date]:
        """
        Generate a key for an article based on its normalized title and date.
        """
        return (
            self._normalize_string(article.title),
            self._normalize_date(article.date),
        )

    def add_article(self, article: Article):
        """
        Add an article to the set of unique articles.

        Args:
            article (Article): The article to add.
        """
        article_id = self._get_article_id(article)
        if article_id and article_id in self.articles_by_id:
            return
        url_str = str(article.url)
        if url_str in self.articles_by_url:
            return
        title_date_key = self._generate_title_date_key(article)
        existing_article = self.articles_by_title_date.get(title_date_key)
        if existing_article:
            existing_body = self._normalize_string(existing_article.body)
            new_body = self._normalize_string(article.body)
            if len(new_body) > len(existing_body):
                self._remove_article_from_all_dicts(existing_article)
                # Re-check uniqueness after removal
                if (
                    self._get_article_id(article) in self.articles_by_id
                    or str(article.url) in self.articles_by_url
                ):
                    return
                self._add_article_to_all_dicts(article, title_date_key)
        else:
            self._add_article_to_all_dicts(article, title_date_key)

    def _add_article_to_all_dicts(
        self, article: Article, title_date_key: Tuple[str, date]
    ):
        article_id = self._get_article_id(article)
        if article_id:
            self.articles_by_id[article_id] = article
        self.articles_by_url[str(article.url)] = article
        self.articles_by_title_date[title_date_key] = article

    def _remove_article_from_all_dicts(self, article: Article):
        article_id = self._get_article_id(article)
        if article_id and article_id in self.articles_by_id:
            del self.articles_by_id[article_id]
        url_str = str(article.url)
        if url_str in self.articles_by_url:
            del self.articles_by_url[url_str]
        title_date_key = self._generate_title_date_key(article)
        if title_date_key in self.articles_by_title_date:
            del self.articles_by_title_date[title_date_key]

    def get_articles(self) -> list[Article]:
        return list(self.articles_by_title_date.values())

    def __iter__(self) -> Iterator[Article]:
        return iter(self.get_articles())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.get_articles()})"

    def __bool__(self) -> bool:
        """
        Return True if the set of unique articles is not empty, False otherwise.

        Returns:
            bool: True if the set of unique articles is not empty, False otherwise.
        """
        return len(self.articles_by_title_date) > 0

    def limit(self, n: int | None) -> "SetOfUniqueArticles":
        """
        Limit the number of articles to be returned. Note: subsequent calls to `add_article` will not be limited.

        Args:
            n (int | None): The maximum number of articles to return. If None, the limit has no effect.

        Returns:
            SetOfUniqueArticles: A new SetOfUniqueArticles instance with the limited number of articles.
        """
        articles = self.get_articles()[:n] if n is not None else self.get_articles()
        return SetOfUniqueArticles(articles)

    def __len__(self) -> int:
        return len(self.articles_by_title_date)

    @overload
    def __getitem__(self, key: int) -> Article: ...

    @overload
    def __getitem__(self, key: slice) -> list[Article]: ...

    def __getitem__(self, key: int | slice) -> Article | List[Article]:
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
            if key < 0 or key >= len(articles):
                raise IndexError("SetOfUniqueArticles index out of range")
            return articles[key]
        return articles[key]
