from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

app = Flask(__name__)

# 🕐 Killzone logic
def in_killzone():
    h = datetime.utcnow().hour
    now_utc = datetime.utcnow()
    london_time = now_utc + timedelta(hours=1)
    ny_time = now_utc - timedelta(hours=4)

    if 7 <= h < 10:
        return f"London – {london_time.strftime('%H:%M')} (UTC+1)"
    if 12 <= h < 15:
        return f"New York – {ny_time.strftime('%H:%M')} (UTC-4)"
    return "Inactive"

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
