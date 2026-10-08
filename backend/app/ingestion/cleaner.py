import re

from bs4 import BeautifulSoup


def strip_html(raw: str) -> str:
    """Remove HTML tags, scripts, nav/ads boilerplate from raw text."""
    if not raw:
        return ""
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    return text


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "")
    return text.strip()


def clean_text(raw: str) -> str:
    """Full cleaning pipeline: HTML stripping + whitespace normalization."""
    no_html = strip_html(raw)
    return normalize_whitespace(no_html)


def validate_article(article: dict) -> bool:
    """Basic validation — reject empty/near-empty or malformed articles."""
    if not article.get("title") or not article.get("content"):
        return False
    if len(article.get("content", "")) < 30:
        return False
    return True
