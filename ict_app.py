from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def in_killzone():
    h = datetime.utcnow().hour
    if 7 <= h < 10: return "London"
    if 12 <= h < 15: return "New York"
    return "Inactive"

dashboard_data = [
    {"pair":"USD/CHF","bias1h":"Bullish","thirty":"","setup15m":"In Discount","fvg":"Yes","ob":"Yes","smt":"Yes","macd":[],"status":"🟢 Ready"},
    {"pair":"EUR/CHF","bias1h":"Bearish","thirty":"","setup15m":"In Premium","fvg":"No","ob":"Yes","smt":"No","macd":[],"status":"🟡 Watching"},
    {"pair":"CHF/JPY","bias1h":"Bearish","thirty":"","setup15m":"Retracement Zone","fvg":"Yes","ob":"No","smt":"Yes","macd":[],"status":"🔴 Not Ready"}
]

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

def get_chf_news():
    return [
        ("Bloomberg: CHF strengthens, SNB ready to intervene", "https://www.bloomberg.com/news/articles/2025-05-06/swiss-franc-has-really-strengthened-a-lot-snb-s-schlegel-says"),
        ("Reuters: USD/CHF Quote", "https://www.reuters.com/markets/quote/USDCHF=X/"),
        ("Bloomberg: Eurovision fans hit by strong CHF", "https://www.bloomberg.com/news/articles/2025-05-10/eurovision-fans-find-swiss-franc-s-latest-surge-hits-a-sour-note"),
        ("FXStreet: USD/CHF Price Analysis", "https://www.fxstreet.com/news/usd-chf-price-analysis-technical-outlook-202406240825"),
        ("FXStreet: CHF drops after SNB rate decision", "https://www.fxstreet.com/news/snb-decision-swiss-franc-weakens-across-board-202406200945"),
        ("FXStreet: CHF Technical Outlook", "https://www.fxstreet.com/news/chf-technical-outlook-franc-under-pressure-amid-risk-appetite-202406191200")
    ]

@app.route('/')
def dashboard():
    news = get_chf_news()
    return render_template_string(open("template.html").read(),
        in_killzone=in_killzone,
        dashboard_data=dashboard_data,
        market_events=market_events,
        news=news
    )

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.json or {}
    pair = payload.get('pair')
    tf   = payload.get('timeframe')
    div  = payload.get('divergence')
    if not pair or not tf or not div:
        return jsonify({"error":"Invalid payload"}), 400
    for row in dashboard_data:
        if row["pair"] == pair:
            row["macd"] = [m for m in row["macd"] if f"({tf})" not in m]
            row["macd"].append(f"{ '🔵' if div == 'Bullish' else '🟠' } {div} ({tf})")
            break
    return jsonify({"message":"Dashboard updated"})

@app.route('/preview')
def preview():
    url = request.args.get('url')
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, timeout=5, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.title.string if soup.title else "No title found"
        desc_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        desc = desc_tag['content'] if desc_tag and 'content' in desc_tag.attrs else "No description available"
        return f"<b>{title}</b><br><small>{desc}</small>", 200
    except:
        return "Unable to load preview", 500

if __name__ == '__main__':
    app.run()
