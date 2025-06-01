import json
from datetime import datetime
import pytz 
import requests 
from pytrends.request import TrendReq 
from datetime import datetime
tw_tz = pytz.timezone("Asia/Taipei")
now = datetime.now(tw_tz).isoformat()

with open("log.txt", "a") as f:
    f.write(f"Crawler ran at {now} Taiwan Time\n")

# 設定時區
tw_tz = pytz.timezone("Asia/Taipei")
now = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

# 抓取台股加權指數
twse_url = "https://www.twse.com.tw/exchangeReport/MI_5MINS_INDEX?response=json&date=&_=0"
twse_response = requests.get(twse_url)
twse_data = twse_response.json()
taiex = twse_data['data'][-1][1]  # 假設收盤價在此位置

# 抓取匯率（台幣對美元）
exchange_url = "https://open.er-api.com/v6/latest/USD"
exchange_response = requests.get(exchange_url)
exchange_data = exchange_response.json()
usd_rate = exchange_data['rates']['TWD']

# 抓取 Google 熱門搜尋趨勢
pytrends = TrendReq(hl='zh-TW', tz=540)
pytrends.build_payload(kw_list=['台股', '匯率', '投資'])
interest_over_time_df = pytrends.interest_over_time()
trends = interest_over_time_df.tail(1).to_dict('records')[0]

# 抓取 Google 熱門搜尋趨勢（前 10 熱門關鍵字及其熱度）
pytrends = TrendReq(hl='en-US', tz=0)
trending_df = pytrends.trending_searches(pn='global')
top_keywords = trending_df[0].head(10).tolist()

# 建立 payload 並取得熱度
pytrends.build_payload(top_keywords, cat=0, timeframe='now 1-H', geo='TW')
interest_df = pytrends.interest_over_time()

# 取最新一筆資料（通常是每分鐘或每小時更新）
latest_row = interest_df.tail(1).to_dict(orient='records')[0]

# 整理成 { 關鍵字: 熱度 }
trends_with_scores = {kw: latest_row.get(kw, 0) for kw in top_keywords}

# 整合資料
data = {
    "time": now,
    "taiex": taiex,
    "usd_rate": usd_rate,
    "trends": trends,
    "top 10 trends": trends_with_scores
}

# 儲存成 JSON
with open("data/data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)