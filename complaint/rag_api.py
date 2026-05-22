# complaint/rag_api.py

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS   # ✅ updated package


def clean(text, max_len=2000):
    if not text:
        return ""
    return " ".join(text.split())[:max_len]


# ----------------------------
# 🌐 DuckDuckGo Web Search
# ----------------------------
def fetch_ddg(query, max_results=5):
    results_data = []

    try:
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=max_results):
                results.append(r)

        for r in results:
            url = r.get("href") or r.get("url") or ""
            title = r.get("title", "")
            snippet = r.get("body", "")

            if not url:
                continue

            results_data.append({
                "source": "ddg",
                "title": title,
                "url": url,
                "snippet": clean(snippet, 400),
                "content": snippet
            })

    except Exception as e:
        print("DDG error:", e)

    return results_data


# ----------------------------
# 📚 Wikipedia Search (Fallback / Backup)
# ----------------------------
def fetch_wikipedia(query, limit=3):
    results = []

    try:
        search_url = "https://en.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json"
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        }

        r = requests.get(search_url, params=params, headers=headers, timeout=10)

        # 🔥 SAFETY CHECK (IMPORTANT)
        if r.status_code != 200:
            print("Wikipedia HTTP error:", r.status_code)
            return []

        try:
            data = r.json()
        except Exception:
            print("Wikipedia returned non-JSON response")
            return []

        for item in data.get("query", {}).get("search", [])[:limit]:
            title = item.get("title", "")
            snippet = item.get("snippet", "")

            page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"

            results.append({
                "source": "wikipedia",
                "title": title,
                "url": page_url,
                "snippet": clean(snippet, 400),
                "content": snippet
            })

    except Exception as e:
        print("Wikipedia error:", e)

    return results


# ----------------------------
# 🔥 HYBRID API RAG
# ----------------------------
def api_web_rag(query, max_results=5):
    ddg_results = fetch_ddg(query, max_results=max_results)

    # If DDG fails → fallback to Wikipedia
    if not ddg_results:
        wiki_results = fetch_wikipedia(query)
        return wiki_results

    # If DDG works → also enrich with Wikipedia (optional boost)
    wiki_results = fetch_wikipedia(query)

    # merge both (DDG priority first)
    return ddg_results + wiki_results