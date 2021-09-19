import requests
import json
from os import path
from datetime import datetime, timedelta
import time

THRESHOLD_FILE = "thresholds.json"

def download_threshold_data():
    if path.exists(THRESHOLD_FILE) and datetime.now() - datetime.fromtimestamp(path.getmtime(THRESHOLD_FILE)) < timedelta(hours=1):
        return
    resp = requests.get("https://tetrio.team2xh.net/data/thresholds.js")
    if resp.status_code == 200:
        js = resp.json()
        relevant_data = dict(date=js['date'], thresholds=js['thresholds'])
        with open(THRESHOLD_FILE, 'w') as f:
           json.dump(relevant_data, f)
        print(f"Updated @ {datetime.now()}")
    else:
        print(f"Ran into issues? Status code: {resp.status_code}")

if __name__ == '__main__':
    while True:
        download_threshold_data()
        time.sleep(5*60)