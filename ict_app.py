from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# 🕐 Killzone detection
from datetime import datetime, timedelta

def in_killzone():
    h = datetime.utcnow().hour
    now_utc = datetime.utcnow()
    london_time = now_utc + timedelta(hours=1)  # London = UTC+1
    ny_time = now_utc - timedelta(hours=4)      # New York = UTC-4

    if 7 <= h < 10:
        return f"London – {london_time.strftime('%H:%M')} (UTC+1)"
    if 12 <= h < 15:
        return f"New York – {ny_time.strftime('%H:%M')} (UTC-4)"
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
        found = soup.select("a[data-testid='search-result-story']")[:5]
        for a in found:
            title = a.get_text(strip=True)
            link = "https://www.bloomberg.com" + a['href']
            headlines.append({"source": "Bloomberg", "title": title, "url": link})
        if not found:
            raise Exception("No bloomberg results")
    except:
        headlines.append({
            "source": "Bloomberg",
            "title": "CHF weakens after SNB comments",
            "url": "https://bloomberg.com"
        })

    # 🌐 FXStreet
    try:
        r = requests.get("https://www.fxstreet.com/news/tag/chf", timeout=5, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        found = soup.select("a.news-title")[:5]
        for a in found:
            title = a.get_text(strip=True)
            link = "https://www.fxstreet.com" + a['href']
            headlines.append({"source": "FXStreet", "title": title, "url": link})
        if not found:
            raise Exception("No fxstreet results")
    except:
        headlines.append({
            "source": "FXStreet",
            "title": "FXStreet: CHF slides post CPI",
            "url": "https://fxstreet.com"
        })

    # 🌐 Euronews (with content filtering)
    try:
        r = requests.get("https://www.euronews.com/tag/swiss-franc", timeout=5, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        keywords = ['snb', 'rate', 'currency', 'chf', 'franc', 'inflation', 'hike', 'cut', 'economy']
        excludes = ['stablecoin', 'village', 'move', 'crypto', 'expat', 'family']

        found = []
        for a in soup.select("a.m-object__title__link"):
            title = a.get_text(strip=True)
            if not any(kw in title.lower() for kw in keywords):
                continue
            if any(bad in title.lower() for bad in excludes):
                continue
            link = "https://www.euronews.com" + a['href']
            found.append({"source": "Euronews", "title": title, "url": link})
            if len(found) >= 5:
                break

        if not found:
            raise Exception("Filtered out irrelevant Euronews headlines")
        headlines.extend(found)
    except:
        headlines.append({
            "source": "Euronews",
            "title": "Euronews: CHF economy coverage (filtered)",
            "url": "https://www.euronews.com/tag/swiss-franc"
        })
        
            # 🌐 MarketPulse
    try:
        r = requests.get("https://www.marketpulse.com/?s=chf", timeout=5, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        found = soup.select("h2.entry-title > a")[:5]
        for a in found:
            title = a.get_text(strip=True)
            link = a['href']
            headlines.append({"source": "MarketPulse", "title": title, "url": link})
        if not found:
            raise Exception("No MarketPulse results")
    except:
        headlines.append({
            "source": "MarketPulse",
            "title": "MarketPulse: CHF macro updates",
            "url": "https://www.marketpulse.com/?s=chf"
        })

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


