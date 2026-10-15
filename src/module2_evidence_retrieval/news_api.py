import requests
import urllib3
import config

urllib3.disable_warnings()


class NewsAPIRetriever:
    """
    NewsAPI Evidence Retriever.
    Only used when a real API key is configured — no simulated fallback.
    Simulated data was generating google.com/search URLs that don't work.
    """
    def __init__(self, api_key=config.NEWS_API_KEY):
        self.api_key = api_key
        self.endpoint = "https://newsapi.org/v2/everything"

    def fetch_articles(self, query: str, pageSize: int = 10):
        """
        Queries NewsAPI for articles matching `query`.
        Returns [] if no API key is configured or request fails.
        """
        if not self.api_key:
            # No API key — skip entirely, no fake fallback
            return []

        try:
            sort_val = "publishedAt" if getattr(config, "ENABLE_RECENCY_RETRIEVAL_PATCH", True) else "relevance"
            import datetime
            from_date = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            params = {
                "q": query,
                "pageSize": pageSize,
                "sortBy": sort_val,
                "from": from_date,
                "language": "en",
                "apiKey": self.api_key
            }
            res = requests.get(
                self.endpoint, params=params, verify=False, timeout=6
            )
            import os
            if os.getenv("DEBUG_TRACE"):
                print(f"[DEBUG_TRACE] NewsAPI HTTP: {res.status_code}")
            if res.status_code == 200:
                data = res.json()
                articles_raw = data.get("articles", [])
                results = []
                for art in articles_raw:
                    title = art.get("title", "").strip()
                    url = art.get("url", "").strip()

                    # Skip removed or empty articles
                    if not title or not url or url == "#" or "removed" in title.lower():
                        continue

                    src_name = art.get("source", {}).get("name", "NewsAPI")
                    domain = url.split("/")[2] if "//" in url else "newsapi.org"

                    results.append({
                        "title": title,
                        "domain": domain,
                        "url": url,
                        "publish_date": art.get("publishedAt", "")[:10],
                        "source": f"NewsAPI ({src_name})",
                        "content": art.get("description", "") or art.get("content", ""),
                        "retrieval_method": "NewsAPI"
                    })
                return results

        except Exception as e:
            print(f"[NewsAPI Notice] {e}")

        return []
