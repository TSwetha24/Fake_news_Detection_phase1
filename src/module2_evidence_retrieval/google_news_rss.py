import requests
import urllib.parse
import urllib3
import xml.etree.ElementTree as ET
import re

urllib3.disable_warnings()


class GoogleNewsRSSRetriever:
    """
    Google News RSS Feed Retriever (100% Free, Real-Time Online News).
    Fetches articles using the FULL claim as a single query, not per keyword.
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_articles(self, query: str, max_records: int = 15):
        """
        Fetches live articles matching `query` from Google News RSS.
        Uses the full claim as one query — no per-keyword splitting.
        """
        all_results = []
        seen_links = set()

        from src.patches import build_recency_query
        q_recency = build_recency_query(query, "google_news")
        queries_to_run = [q_recency] if q_recency != query else [query]
        if query not in queries_to_run:
            queries_to_run.append(query)
        # Also try a condensed version (first 8 words) as fallback for long claims
        words = query.split()
        if len(words) > 6:
            queries_to_run.append(" ".join(words[:8]))

        for q in queries_to_run:
            encoded = urllib.parse.quote(q)
            url = (
                f"https://news.google.com/rss/search?q={encoded}"
                f"&hl=en-IN&gl=IN&ceid=IN:en"
            )

            try:
                resp = requests.get(url, headers=self.headers, verify=False, timeout=2.5)
                import os
                if os.getenv("DEBUG_TRACE"):
                    print(f"[DEBUG_TRACE] Google News HTTP: {resp.status_code}")
                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    items = root.findall('.//item')

                    for item in items:
                        title_el = item.find('title')
                        link_el = item.find('link')
                        pubDate_el = item.find('pubDate')
                        source_el = item.find('source')

                        title = title_el.text.strip() if title_el is not None and title_el.text else ""
                        link = link_el.text.strip() if link_el is not None and link_el.text else "#"
                        pubDate = pubDate_el.text[:16] if pubDate_el is not None and pubDate_el.text else "Unknown"
                        source_name = source_el.text.strip() if source_el is not None and source_el.text else "Google News"

                        # Skip empty titles or obviously bad links
                        if not title or link == "#" or not link.startswith("http"):
                            continue

                        domain = link.split("/")[2] if "//" in link else "news.google.com"

                        if link not in seen_links:
                            seen_links.add(link)
                            all_results.append({
                                "title": title,
                                "domain": domain,
                                "url": link,
                                "publish_date": pubDate,
                                "source": f"Google News ({source_name})",
                                "content": f"Live Google News: '{title}' — {source_name}.",
                                "retrieval_method": "Google News RSS API"
                            })

                        if len(all_results) >= max_records:
                            break

            except Exception as e:
                print(f"[Google News RSS Notice] {e}")

            if len(all_results) >= max_records:
                break

        return all_results[:max_records]
