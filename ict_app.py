from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# 🕐 Killzone detection
from datetime import datetime
def in_killzone():
    h = datetime.utcnow().hour
    if 7 <= h < 10: return "London"
    if 12 <= h < 15: return "New York"
    return "Inactive"

# 📊 Main dashboard data
dashboard_data = [
    {"pair":"USD/CHF","bias1h":"Bullish","thirty":"","setup15m":"In Discount","fvg":"Yes","ob":"Yes","smt":"Yes","macd":[],"status":"🟢 Ready"},
    {"pair":"EUR/CHF","bias1h":"Bearish","thirty":"","setup15m":"In Premium","fvg":"No","ob":"Yes","smt":"No","macd":[],"status":"🟡 Watching"},
    {"pair":"CHF/JPY","bias1h":"Bearish","thirty":"","setup15m":"Retracement Zone","fvg":"Yes","ob":"No","smt":"Yes","macd":[],"status":"🔴 Not Ready"}
]

# 📉 Market events & reasons
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

# 🔁 CHF News Function + Endpoint
def fetch_chf_news():
    headlines = []
    headers = {"User-Agent": "Mozilla/5.0"}

    # 🌐 Bloomberg
    try:
        r = requests.get("https://www.bloomberg.com/search?query=chf", timeout=5, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a[data-testid='search-result-story']")[:5]:
            title = a.get_text(strip=True)
            link = "https://www.bloomberg.com" + a['href']
            headlines.append({"source": "Bloomberg", "title": title, "url": link})
    except:
        headlines.append({"source": "Bloomberg", "title": "⚠️ Bloomberg CHF feed unavailable", "url": "#"})

    # 🌐 FXStreet
    try:
        r = requests.get("https://www.fxstreet.com/news/tag/chf", timeout=5, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a.news-title")[:5]:
            title = a.get_text(strip=True)
            link = "https://www.fxstreet.com" + a['href']
            headlines.append({"source": "FXStreet", "title": title, "url": link})
    except:
        headlines.append({"source": "FXStreet", "title": "⚠️ FXStreet CHF feed unavailable", "url": "#"})

    # 🌐 ForexLive
    try:
        r = requests.get("https://www.forexlive.com/Tags/chf/", timeout=5, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a.tag-article-title")[:5]:
            title = a.get_text(strip=True)
            link = "https://www.forexlive.com" + a['href']
            headlines.append({"source": "ForexLive", "title": title, "url": link})
    except:
        headlines.append({"source": "ForexLive", "title": "⚠️ ForexLive CHF feed unavailable", "url": "#"})

    # 🌐 Euronews
    try:
        r = requests.get("https://www.euronews.com/tag/swiss-franc", timeout=5, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a.m-object__title__link")[:5]:
            title = a.get_text(strip=True)
            link = "https://www.euronews.com" + a['href']
            headlines.append({"source": "Euronews", "title": title, "url": link})
    except:
        headlines.append({"source": "Euronews", "title": "⚠️ Euronews CHF feed unavailable", "url": "#"})

    # 🌐 Economies.com
    try:
        r = requests.get("https://www.economies.com/news/tag/CHF", timeout=5, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("div.details > h3 > a")[:5]:
            title = a.get_text(strip=True)
            link = "https://www.economies.com" + a['href']
            headlines.append({"source": "Economies.com", "title": title, "url": link})
    except:
        headlines.append({"source": "Economies.com", "title": "⚠️ Economies.com CHF feed unavailable", "url": "#"})

    # 🌐 DailyForex
    try:
        r = requests.get("https://www.dailyforex.com/search-results?search=chf", timeout=5, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("div.search-post h3 a")[:5]:
            title = a.get_text(strip=True)
            link = "https://www.dailyforex.com" + a['href']
            headlines.append({"source": "DailyForex", "title": title, "url": link})
    except:
        headlines.append({"source": "DailyForex", "title": "⚠️ DailyForex CHF feed unavailable", "url": "#"})

    return headlines

@app.route("/get_news")
def get_news():
    return jsonify(fetch_chf_news())

# 🧠 Main page route
@app.route("/")
def dashboard():
    return render_template("template.html", in_killzone=in_killzone, dashboard_data=dashboard_data, market_events=market_events)

if __name__ == "__main__":
    app.run(debug=True)


