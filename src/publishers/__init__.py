"""Publishers package for OpenDataAnalysisTokouynu."""
from src.publishers.base import BasePublisher
from src.publishers.markdown_file import MarkdownFilePublisher
from src.publishers.wordpress_mail import WordPressMailPublisher
from src.publishers.wordpress_rest import WordPressRestPublisher

__all__ = [
    "BasePublisher",
    "MarkdownFilePublisher",
    "WordPressMailPublisher",
    "WordPressRestPublisher",
]
