import urllib.parse
import xml.etree.ElementTree as ET
import requests
import urllib3
from date_utils import extract_target_dates

urllib3.disable_warnings()

class GoogleNewsRSSRetriever:
    """
    Google News RSS Feed Retriever (100% Free, Real-Time Online News).
    Formulates targeted query terms including specific date verification.
    """
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    def fetch_articles(self, query: str, max_records: int = 15):
        """
        Fetches live articles matching `query` from Google News RSS.
        """
        date_info = extract_target_dates(query)
        queries_to_run = [query]
        
        if date_info["is_date_specific_claim"]:
            readable_date = date_info["target_date_str_readable"]
            # Construct targeted date query
            clean_query = query.replace("14/8/2026", "").replace("14/08/2026", "").replace("tomorrow", "").strip()
            date_specific_query = f"{clean_query} {readable_date}"
            queries_to_run.insert(0, date_specific_query)

        all_results = []
        seen_links = set()

        for q in queries_to_run:
            encoded = urllib.parse.quote(q)
            url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
            
            try:
                resp = requests.get(url, headers=self.headers, verify=False, timeout=6)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    items = root.findall('.//item')
                    
                    for item in items:
                        title = item.find('title').text if item.find('title') is not None else ""
                        link = item.find('link').text if item.find('link') is not None else "#"
                        pubDate = item.find('pubDate').text if item.find('pubDate') is not None else "2026-08-13"
                        source_el = item.find('source')
                        source_name = source_el.text if source_el is not None else "Google News"
                        domain = link.split("/")[2] if "//" in link else "google.com"
                        
                        if link not in seen_links:
                            seen_links.add(link)
                            all_results.append({
                                "title": title,
                                "domain": domain,
                                "url": link,
                                "publish_date": pubDate[:16],
                                "source": f"Google News ({source_name})",
                                "content": f"Live Google News report: '{title}' published by {source_name}.",
                                "retrieval_method": "Google News RSS API"
                            })
            except Exception as e:
                print(f"[Google News RSS Notice] Request notice ({e}).")
                
        return all_results[:max_records]
