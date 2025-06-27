from flask import Flask, render_template, jsonify
from bs4 import BeautifulSoup
import requests
from datetime import datetime

app = Flask(__name__)

# ✅ Killzone logic
def in_killzone():
    h = datetime.utcnow().hour
    if 7 <= h < 10: return "London"
    if 12 <= h < 15: return "New York"
    return "Inactive"

# ✅ Dummy dashboard data
dashboard_data = [
    {"pair":"USD/CHF","bias1h":"Bullish","thirty":"","setup15m":"In Discount","fvg":"Yes","ob":"Yes","smt":"Yes","macd":[],"status":"🟢 Ready"},
    {"pair":"EUR/CHF","bias1h":"Bearish","thirty":"","setup15m":"In Premium","fvg":"No","ob":"Yes","smt":"No","macd":[],"status":"🟡 Watching"},
    {"pair":"CHF/JPY","bias1h":"Bearish","thirty":"","setup15m":"Retracement Zone","fvg":"Yes","ob":"No","smt":"Yes","macd":[],"status":"🔴 Not Ready"}
]

# ✅ Static market event explanations
market_events = [
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
    },
    {
        "event":"US CPI Above Expectations",
        "reactions":[
            {"pair":"USD/JPY","reaction":"🚀 Goes up"},
            {"pair":"EUR/USD","reaction":"📉 Goes down"},
            {"pair":"Gold/USD","reaction":"📉 Goes down"}
        ],
        "reasons":[
            {"reason":"🔺 Higher Inflation","explanation":"Boosts expectations of Fed rate hikes."},
            {"reason":"💰 Bond Sell-Off","explanation":"Rising yields favor USD."},
            {"reason":"🧭 Fed Hawkish","explanation":"Tighter policy outlook increases USD strength."}
        ]
    },
    {
        "event":"Geopolitical Risk: Israel–Iran Conflict",
        "reactions":[
            {"pair":"Gold/USD","reaction":"🚀 Goes up (safe-haven flow)"},
            {"pair":"USD/JPY","reaction":"📉 Goes down"},
            {"pair":"Oil/USD","reaction":"🚀 Goes up"}
        ],
        "reasons":[
            {"reason":"☢️ War Risk Premium","explanation":"Gold & oil spike on uncertainty."},
            {"reason":"🛡️ Safe Haven Bid","explanation":"JPY and Gold gain strength."},
            {"reason":"⛽ Oil Supply Fears","explanation":"Middle East tension lifts crude prices."}
        ]
    }
]

# ✅ CHF News Scraper
def fetch_chf_news():
    headlines = []
    try:
        r = requests.get("https://www.bloomberg.com/search?query=chf")
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a[data-testid='search-result-story']")[:5]:
            title = a.get_text(strip=True)
            link = "https://www.bloomberg.com" + a['href']
            headlines.append({"source": "Bloomberg", "title": title, "url": link})
    except:
        headlines.append({"source": "Bloomberg", "title": "⚠️ Failed to load", "url": "#"})

    try:
        r = requests.get("https://www.fxstreet.com/news/tag/chf")
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a.news-title")[:5]:
            title = a.get_text(strip=True)
            link = "https://www.fxstreet.com" + a['href']
            headlines.append({"source": "FXStreet", "title": title, "url": link})
    except:
        headlines.append({"source": "FXStreet", "title": "⚠️ Failed to load", "url": "#"})

    return headlines

@app.route("/")
def dashboard():
    return render_template("template.html", in_killzone=in_killzone, dashboard_data=dashboard_data, market_events=market_events)

@app.route("/get_news")
def get_news():
    return jsonify(fetch_chf_news())

