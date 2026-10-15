import urllib.parse
import requests
import urllib3
import re

urllib3.disable_warnings()


class DuckDuckGoNewsRetriever:
    """
    DuckDuckGo Web & News Search (100% Free, No API Key).
    Extracts real article titles and URLs, not just generic snippets.
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_articles(self, query: str, max_records: int = 8):
        """
        Queries DuckDuckGo HTML search. Extracts real titles and links — 
        not the query string repeated as a fake title.
        """
        encoded = urllib.parse.quote(query)
        import config
        df_param = "&df=w" if getattr(config, "ENABLE_RECENCY_RETRIEVAL_PATCH", True) else ""
        url = f"https://html.duckduckgo.com/html/?q={encoded}{df_param}"

        try:
            resp = requests.get(url, headers=self.headers, verify=False, timeout=3.5)
            import os
            if os.getenv("DEBUG_TRACE"):
                print(f"[DEBUG_TRACE] DuckDuckGo HTTP: {resp.status_code}")
            if resp.status_code == 200:
                html = resp.text

                # Extract result blocks: title + link + snippet
                # DuckDuckGo HTML structure: result__a (title+link), result__snippet
                title_link_matches = re.findall(
                    r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
                    html, re.DOTALL
                )
                snippet_matches = re.findall(
                    r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
                    html, re.DOTALL
                )

                results = []
                for idx, (link, title_raw) in enumerate(title_link_matches[:max_records]):
                    title = re.sub(r'<[^>]+>', '', title_raw).strip()
                    snippet = ""
                    if idx < len(snippet_matches):
                        snippet = re.sub(r'<[^>]+>', '', snippet_matches[idx]).strip()

                    # Resolve DuckDuckGo redirect URLs
                    if link.startswith("//duckduckgo.com/l/?uddg="):
                        link_parsed = urllib.parse.parse_qs(
                            urllib.parse.urlparse(link.replace("//", "https://")).query
                        )
                        link = urllib.parse.unquote(link_parsed.get("uddg", [link])[0])

                    if not link.startswith("http") or not title:
                        continue

                    domain = link.split("/")[2] if "//" in link else "duckduckgo.com"

                    # Skip DDG-internal pages
                    if "duckduckgo.com" in domain:
                        continue

                    results.append({
                        "title": title,
                        "domain": domain,
                        "url": link,
                        "publish_date": "Live Search",
                        "source": f"DuckDuckGo ({domain})",
                        "content": snippet or f"Web search result: {title}",
                        "retrieval_method": "DuckDuckGo API"
                    })

                if results:
                    return results

        except Exception as e:
            print(f"[DuckDuckGo API Notice] {e}")

        return []
