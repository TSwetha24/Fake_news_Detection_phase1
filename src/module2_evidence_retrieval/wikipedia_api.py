import urllib.parse
import requests
import urllib3
import re

urllib3.disable_warnings()

class WikipediaAPIRetriever:
    """
    Wikipedia Knowledge Search API (100% Free Fact Verification).
    Queries Wikipedia API for encyclopedic evidence and entity fact verification.
    """
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        self.api_url = "https://en.wikipedia.org/w/api.php"

    def fetch_articles(self, query: str, max_records: int = 5):
        """
        Queries Wikipedia API for entries related to `query`.
        """
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": max_records
        }
        
        try:
            resp = requests.get(self.api_url, params=params, headers=self.headers, verify=False, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("query", {}).get("search", [])
                
                results = []
                for item in items:
                    title = item.get("title", "")
                    snippet_html = item.get("snippet", "")
                    snippet = re.sub(r'<[^>]+>', '', snippet_html) # strip HTML tags
                    pageid = item.get("pageid", "")
                    
                    results.append({
                        "title": f"Wikipedia Entry: {title}",
                        "domain": "en.wikipedia.org",
                        "url": f"https://en.wikipedia.org/?curid={pageid}",
                        "publish_date": "Verified Reference",
                        "source": "Wikipedia Knowledge Base",
                        "content": f"Encyclopedic factual reference for '{title}': {snippet}",
                        "retrieval_method": "Wikipedia Search API"
                    })
                return results
        except Exception as e:
            print(f"[Wikipedia API Notice] Request notice ({e}).")

        return []
