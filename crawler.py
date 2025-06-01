import json
from datetime import datetime
import pytz
import requests
from pytrends.request import TrendReq

# 設定時區
tw_tz = pytz.timezone("Asia/Taipei")
now = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

# 抓取台股加權指數
twse_url = "https://www.twse.com.tw/exchangeReport/MI_5MINS_INDEX?response=json&date=&_=0"
twse_response = requests.get(twse_url)
twse_data = twse_response.json()
taiex = twse_data['data'][-1][1]  # 假設收盤價在此位置

# 抓取匯率（台幣對美元）
exchange_url = "https://api.exchangerate-api.com/v4/latest/TWD"
exchange_response = requests.get(exchange_url)
exchange_data = exchange_response.json()
usd_rate = exchange_data['rates']['USD']

# 抓取 Google 熱門搜尋趨勢
pytrends = TrendReq(hl='zh-TW', tz=540)
pytrends.build_payload(kw_list=['台股', '匯率', '投資'])
interest_over_time_df = pytrends.interest_over_time()
trends = interest_over_time_df.tail(1).to_dict('records')[0]

# 整合資料
data = {
    "time": now,
    "taiex": taiex,
    "usd_rate": usd_rate,
    "trends": trends
}

# 儲存成 JSON
with open("data/data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)