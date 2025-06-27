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

# 🔁 CHF News Function
def fetch_chf_news():
    headlines = []
    headers = {"User-Agent": "Mozilla/5.0"}

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
        headlines.append({"source": "Bloomberg", "title": "CHF weakens after SNB comments", "url": "https://bloomberg.com"})

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
        headlines.append({"source": "FXStreet", "title": "FXStreet: CHF slides post CPI", "url": "https://fxstreet.com"})

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
                row["macd"] = f"{'🔵' if div == 'Bullish' else '🟠'} {div}"
                row["status"] = "<span class='status-box green'>🟢 Ready</span>" if div == "Bullish" else "<span class='status-box red'>🔴 Not Ready</span>"
            break

    return jsonify({"message": "MACD divergence updated"})
