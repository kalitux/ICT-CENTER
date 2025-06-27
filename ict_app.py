from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

app = Flask(__name__)

# 🕐 Killzone logic
def in_killzone():
    now_utc = datetime.utcnow()
    h = now_utc.hour
    london_label = "London 🕐‣ 3 AM – 6 AM"
    ny_label = "New York 🕐‣ 8 AM – 11 AM"

    if 7 <= h < 10:
        return f"{london_label} ({now_utc.strftime('%H:%M')} UTC)"
    if 12 <= h < 15:
        return f"{ny_label} ({now_utc.strftime('%H:%M')} UTC)"
    return f"Inactive ({now_utc.strftime('%H:%M')} UTC)"

# 📊 Dashboard Data
dashboard_data = [
    {"pair": "USD/CHF", "bias1h": "🔵 Bullish", "bias30m": "🟠 Bearish", "setup15m": "—", "fvg": "Yes", "ob": "Yes", "smt": "Confirmed", "macd": "", "status": "<span class='status-box yellow'>🟡 Watching</span>"},
    {"pair": "EUR/CHF", "bias1h": "🟠 Bearish", "bias30m": "🔵 Bullish", "setup15m": "Retracement", "fvg": "No", "ob": "Yes", "smt": "Watching", "macd": "", "status": "<span class='status-box yellow'>🟡 Watching</span>"},
    {"pair": "CHF/JPY", "bias1h": "🟠 Bearish", "bias30m": "🟠 Bearish", "setup15m": "—", "fvg": "Yes", "ob": "No", "smt": "Confirmed", "macd": "", "status": "<span class='status-box yellow'>🟡 Watching</span>"}
]

# 🔁 CHF News Function + Endpoint
def fetch_chf_news():
    headlines = []

    headers = {"User-Agent": "Mozilla/5.0"}

  # 🌐 TradingView News
    try:
        r = requests.get("https://www.tradingview.com/news/", timeout=5, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        found = []
        for a in soup.select("a.tv-widget-news__item"):
            title = a.get_text(strip=True)
            link = "https://www.tradingview.com" + a['href']
            if any(tag in title.lower() for tag in ['swiss', 'chf', 'franc']):
                found.append({"source": "TradingView", "title": title, "url": link})
            if len(found) >= 5:
                break

        if not found:
            raise Exception("No CHF-related TradingView articles found")
        headlines.extend(found)
    except:
        headlines.append({
            "source": "TradingView",
            "title": "TradingView: General market updates",
            "url": "https://www.tradingview.com/news/"
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
        
    return headlines

@app.route("/")
def dashboard():
    return render_template("template.html", in_killzone=in_killzone, dashboard_data=dashboard_data, market_events=[])

@app.route("/get_news")
def get_news():
    return jsonify(fetch_chf_news())

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    pair = data.get("pair")
    tf = data.get("timeframe")
    div = data.get("divergence")

    if not (pair and tf and div):
        return jsonify({"error": "Invalid payload"}), 400

    for row in dashboard_data:
        if row["pair"] == pair:
            if tf == "15M":
                timestamp = datetime.utcnow().strftime('%H:%M')
                label = f"{'🔵' if div == 'Bullish' else '🟠'} {div} ({timestamp} UTC)"
                row["macd"] = f"<span class='live-macd'>{label}</span>"
                row["status"] = "<span class='status-box green'>🟢 Ready</span>"
            break

    return jsonify({"message": "MACD divergence updated"})
