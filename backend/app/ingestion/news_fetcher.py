"""
Fetches financial news either from a real News API (if NEWS_API_KEY is set)
or from a built-in mock/demo dataset so the project runs end-to-end without
any external credentials.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


_MOCK_ARTICLES: List[Dict[str, Any]] = [
    {
        "title": "Central Bank Holds Interest Rates Steady Amid Inflation Concerns",
        "description": "The central bank kept benchmark rates unchanged, citing persistent inflation.",
        "content": (
            "The central bank announced today that it will hold its benchmark interest rate steady, "
            "citing ongoing concerns about inflation that remains above target. Policymakers noted that "
            "while inflation has cooled from its peak, price pressures in housing and services remain "
            "elevated. Analysts expect the bank to maintain a cautious stance for the next two quarters, "
            "watching labor market data closely before considering any rate cuts. Banking sector stocks "
            "reacted mildly, with major lenders seeing a slight uptick as steady rates support net "
            "interest margins in the near term."
        ),
        "source": "Reuters", "author": "Financial Desk", "category": "monetary-policy",
        "ticker": None, "url": "https://example.com/news/central-bank-holds-rates",
        "published_at": datetime.utcnow() - timedelta(days=1),
    },
    {
        "title": "Banking Sector Faces Headwinds from Rising Loan Defaults",
        "description": "Regional banks report an uptick in non-performing loans amid economic slowdown.",
        "content": (
            "Several regional banks reported a noticeable increase in non-performing loans in their "
            "latest quarterly filings, raising concerns about credit quality as economic growth slows. "
            "Commercial real estate loans were flagged as a particular area of weakness, with vacancy "
            "rates in office space remaining high post-pandemic. Regulators have urged banks to build "
            "additional loan-loss reserves. Despite the headwinds, larger diversified banks with strong "
            "capital buffers are seen as better positioned to absorb potential losses compared to smaller, "
            "regionally concentrated lenders."
        ),
        "source": "Financial Times", "author": "Banking Correspondent", "category": "banking",
        "ticker": None, "url": "https://example.com/news/banking-sector-headwinds",
        "published_at": datetime.utcnow() - timedelta(days=2),
    },
    {
        "title": "Understanding Inflation: What It Means for Everyday Investors",
        "description": "An educational overview of inflation and its effects on savings and investments.",
        "content": (
            "Inflation refers to the general increase in prices of goods and services over time, which "
            "erodes purchasing power. For everyday investors, inflation matters because it reduces the "
            "real return on cash savings and fixed-income investments. Historically, equities and "
            "inflation-protected securities such as TIPS have offered some degree of protection against "
            "inflation, though outcomes vary by market cycle. Diversification across asset classes is "
            "commonly cited as a way to manage inflation risk, though it does not eliminate it. Investors "
            "are generally advised to review their portfolio allocation periodically rather than reacting "
            "to short-term inflation prints."
        ),
        "source": "Investopedia", "author": "Editorial Team", "category": "education",
        "ticker": None, "url": "https://example.com/education/understanding-inflation",
        "published_at": datetime.utcnow() - timedelta(days=5),
    },
    {
        "title": "Tech Giant Reports Strong Quarterly Earnings, Beats Estimates",
        "description": "Shares rise after the company posts better-than-expected revenue and profit.",
        "content": (
            "A major technology company reported quarterly earnings that beat analyst expectations, "
            "driven by strong cloud computing revenue and resilient consumer demand. The company's "
            "operating margin expanded year-over-year, and management raised full-year guidance. "
            "Shares climbed in after-hours trading following the announcement. Analysts noted that "
            "continued investment in AI infrastructure is a key growth driver but cautioned that rising "
            "capital expenditure could pressure free cash flow in coming quarters."
        ),
        "source": "Bloomberg", "author": "Markets Team", "category": "earnings",
        "ticker": "TECH", "url": "https://example.com/news/tech-earnings-beat",
        "published_at": datetime.utcnow() - timedelta(days=3),
    },
    {
        "title": "How Diversification Helps Manage Investment Risk",
        "description": "A primer on portfolio diversification strategies for retail investors.",
        "content": (
            "Diversification is an investment strategy that spreads capital across different asset "
            "classes, sectors, and geographies to reduce the impact of any single investment's poor "
            "performance on an overall portfolio. Common approaches include mixing stocks and bonds, "
            "investing across multiple industries, and adding international exposure. While "
            "diversification can reduce unsystematic risk, it does not protect against broad market "
            "downturns (systematic risk). Financial educators generally recommend that individuals "
            "assess their risk tolerance and time horizon before deciding on an asset allocation, and "
            "consider consulting a licensed financial advisor for personalized guidance."
        ),
        "source": "Banking Website", "author": "Editorial", "category": "education",
        "ticker": None, "url": "https://example.com/education/diversification",
        "published_at": datetime.utcnow() - timedelta(days=7),
    },
    {
        "title": "Stock Market Volatility Rises Amid Global Trade Tensions",
        "description": "Equity markets swing as investors weigh new tariff announcements.",
        "content": (
            "Global equity markets experienced heightened volatility this week following the "
            "announcement of new tariffs between major trading partners. Sectors with significant "
            "international supply chain exposure, such as manufacturing and semiconductors, were "
            "among the hardest hit. Safe-haven assets, including government bonds and gold, saw "
            "increased inflows as investors sought to reduce risk. Market strategists caution that "
            "continued uncertainty around trade policy could keep volatility elevated in the near term, "
            "and recommend investors avoid making drastic portfolio changes based on short-term "
            "headlines."
        ),
        "source": "Reuters", "author": "Markets Desk", "category": "markets",
        "ticker": None, "url": "https://example.com/news/trade-tension-volatility",
        "published_at": datetime.utcnow() - timedelta(hours=12),
    },
]


class NewsFetcher:
    """Fetches financial news from a real API when configured, else mock data."""

    def __init__(self):
        self.api_key = settings.NEWS_API_KEY
        self.api_url = settings.NEWS_API_URL
        self.mock_mode = settings.news_mock_mode

    def fetch(self, query: str = "finance OR banking OR markets", page_size: int = 20) -> List[Dict[str, Any]]:
        if self.mock_mode:
            logger.info("NEWS_API_KEY not set — running ingestion in mock/demo data mode.")
            return _MOCK_ARTICLES
        return self._fetch_from_api(query=query, page_size=page_size)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def _fetch_from_api(self, query: str, page_size: int) -> List[Dict[str, Any]]:
        logger.info("Fetching financial news from external API...")
        params = {"q": query, "apiKey": self.api_key, "pageSize": page_size, "language": "en", "sortBy": "publishedAt"}
        response = requests.get(self.api_url, params=params, timeout=15)
        response.raise_for_status()
        payload = response.json()
        articles = payload.get("articles", [])
        logger.info(f"Fetched {len(articles)} articles from news API.")

        normalized = []
        for a in articles:
            normalized.append({
                "title": a.get("title") or "Untitled",
                "description": a.get("description"),
                "content": a.get("content") or a.get("description") or "",
                "source": (a.get("source") or {}).get("name"),
                "author": a.get("author"),
                "category": None,
                "ticker": None,
                "url": a.get("url"),
                "published_at": a.get("publishedAt"),
            })
        return normalized
