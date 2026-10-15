import requests
import urllib.parse
import urllib3
import config

urllib3.disable_warnings()


class GDELTNewsRetriever:
    """
    GDELT DOC API v2 Evidence Retriever.
    Only returns real GDELT results — NO simulated fallback data.
    Simulated data with fake URLs was causing non-working links.
    """
    def __init__(self, api_url=config.GDELT_API_URL):
        self.api_url = api_url

    def fetch_articles(self, query: str, max_records: int = 10):
        """
        Queries GDELT API for online news articles related to the claim query.
        Returns [] if GDELT is unavailable (no simulated fallback).
        """
        params = {
            "query": query,
            "mode": "artlist",
            "maxrecords": max_records,
            "format": "json",
            "sort": "DateDesc"
        }
        if getattr(config, "ENABLE_RECENCY_RETRIEVAL_PATCH", True):
            params["timespan"] = "7d"

        try:
            response = requests.get(
                self.api_url, params=params, verify=False, timeout=4.5
            )
            import os
            if os.getenv("DEBUG_TRACE"):
                print(f"[DEBUG_TRACE] GDELT HTTP: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                articles_raw = data.get("articles", [])

                results = []
                for item in articles_raw:
                    title = item.get("title", "").strip()
                    url = item.get("url", "").strip()
                    domain = item.get("domain", "").strip()

                    # Skip entries with no real title or URL
                    if not title or not url or not url.startswith("http"):
                        continue

                    if not domain:
                        domain = url.split("/")[2] if "//" in url else "gdeltproject.org"

                    results.append({
                        "title": title,
                        "domain": domain,
                        "url": url,
                        "publish_date": item.get("seendate", "Recent")[:10],
                        "source": f"GDELT ({domain})",
                        "content": f"Global media coverage: '{title}' — reported by {domain}.",
                        "retrieval_method": "GDELT API v2"
                    })

                return results

        except Exception as e:
            print(f"[GDELT API Notice] {e}")

        # No simulated fallback — return empty so fake links don't appear
        return []
