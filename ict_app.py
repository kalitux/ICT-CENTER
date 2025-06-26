# 🔁 CHF News Function + Endpoint
from bs4 import BeautifulSoup
import requests

def fetch_chf_news():
    headlines = []

    # 🌐 Bloomberg CHF News
    try:
        bloom = requests.get("https://www.bloomberg.com/search?query=chf")
        soup = BeautifulSoup(bloom.text, "html.parser")
        for a in soup.select("a[data-testid='search-result-story']")[:5]:
            title = a.get_text(strip=True)
            link = "https://www.bloomberg.com" + a['href']
            headlines.append({"source": "Bloomberg", "title": title, "url": link})
    except:
        headlines.append({"source": "Bloomberg", "title": "⚠️ Failed to load", "url": "#"})

    # 🌐 FXStreet CHF News
    try:
        fx = requests.get("https://www.fxstreet.com/news/tag/chf")
        soup = BeautifulSoup(fx.text, "html.parser")
        for a in soup.select("a.news-title")[:5]:
            title = a.get_text(strip=True)
            link = "https://www.fxstreet.com" + a['href']
            headlines.append({"source": "FXStreet", "title": title, "url": link})
    except:
        headlines.append({"source": "FXStreet", "title": "⚠️ Failed to load", "url": "#"})

    return headlines

@app.route("/get_news")
def get_news():
    return jsonify(fetch_chf_news())
