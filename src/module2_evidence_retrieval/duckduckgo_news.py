import urllib.parse
import requests
import urllib3
import re

urllib3.disable_warnings()

class DuckDuckGoNewsRetriever:
    """
    DuckDuckGo Web & News Search API (100% Free, No API Key Required).
    Fetches real-time web search results and news snippets.
    """
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    def fetch_articles(self, query: str, max_records: int = 10):
        """
        Queries DuckDuckGo HTML search for instant web evidence.
        """
        encoded = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        
        try:
            resp = requests.get(url, headers=self.headers, verify=False, timeout=6)
            if resp.status_code == 200:
                html = resp.text
                # Simple regex extraction of titles and snippets from DuckDuckGo HTML results
                matches = re.findall(r'<a class="result__url"[^>]*href="([^"]+)"[^>]*>.*?</a>.*?<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
                
                results = []
                for idx, (link, snippet_raw) in enumerate(matches[:max_records]):
                    snippet = re.sub(r'<[^>]+>', '', snippet_raw).strip()
                    domain = link.split("/")[2] if "//" in link else "duckduckgo.com"
                    
                    results.append({
                        "title": f"Web Search Evidence #{idx+1}: {query}",
                        "domain": domain,
                        "url": link,
                        "publish_date": "Live Search Result",
                        "source": f"DuckDuckGo Web Search ({domain})",
                        "content": snippet or f"Web search match for '{query}' on {domain}.",
                        "retrieval_method": "DuckDuckGo API"
                    })
                if results:
                    return results
        except Exception as e:
            print(f"[DuckDuckGo API Notice] Request notice ({e}).")

        return []
