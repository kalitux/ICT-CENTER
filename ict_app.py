from flask import Flask, request, jsonify, render_template_string
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

# 🔁 Killzone logic
def in_killzone():
    h = datetime.utcnow().hour
    if 7 <= h < 10: return "London"
    if 12 <= h < 15: return "New York"
    return "Inactive"

# 🔁 Dashboard mock data
dashboard_data = [
    {"pair":"USD/CHF","bias1h":"Bullish","thirty":"","setup15m":"In Discount","fvg":"Yes","ob":"Yes","smt":"Yes","macd":[],"status":"🟢 Ready"},
    {"pair":"EUR/CHF","bias1h":"Bearish","thirty":"","setup15m":"In Premium","fvg":"No","ob":"Yes","smt":"No","macd":[],"status":"🟡 Watching"},
    {"pair":"CHF/JPY","bias1h":"Bearish","thirty":"","setup15m":"Retracement Zone","fvg":"Yes","ob":"No","smt":"Yes","macd":[],"status":"🔴 Not Ready"}
]

# 🔁 Market reaction modules
market_events = [  # (You can keep your long market_events here as before)
    {
        "event":"Swiss National Bank Rate Cut",
        "reactions":[
            {"pair":"USD/CHF","reaction":"🚀 Goes up (USD strengthens vs CHF)"},
            {"pair":"EUR/CHF","reaction":"🚀 Goes up"},
            {"pair":"CHF/JPY","reaction":"📉 Goes down (CHF weakens vs JPY)"}
        ],
        "reasons":[
            {"reason":"📉 Lower Yield","explanation":"Rate cut = lower returns on CHF."},
            {"reason":"💸 Capital Outflows","explanation":"Investors shift to higher yields."},
            {"reason":"📊 Dovish SNB","explanation":"Central bank stimulating economy."},
            {"reason":"🏦 Carry Trade","explanation":"CHF shorting becomes cheaper."}
        ]
    }
]

# ✅ CHF News Function + Endpoint
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

# ✅ MAIN ROUTE
@app.route('/')
def dashboard():
    return render_template_string(
        "<h1>ICT Command Center Running</h1><p>Go to /get_news for CHF news feed.</p>",
        in_killzone=in_killzone,
        dashboard_data=dashboard_data,
        market_events=market_events
    )

if __name__ == "__main__":
    app.run()
