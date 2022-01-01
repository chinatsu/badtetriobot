import requests
import json
from os import path
from datetime import datetime, timedelta
import time

THRESHOLD_FILE = "thresholds.json"

def fetch_complete_leaderboard():
    resp = requests.get("https://ch.tetr.io/api/users/lists/league/all")
    if resp.status_code == 200:
        js = resp.json()
        return js
    else:
        return None

def sort_players_into_buckets(lb):
    min_tr = {"x": 99999.0, "u": 99999.0, "ss": 99999.0, "s+": 99999.0, "s": 99999.0, "s-": 99999.0, "a+": 99999.0, "a": 99999.0, "a-": 99999.0, "b+": 99999.0, "b": 99999.0, "b-": 99999.0, "c+": 99999.0, "c": 99999.0, "c-": 99999.0, "d+": 99999.0, "d": 99999.0}
    counters = {"x": 0, "u": 0, "ss": 0, "s+": 0, "s": 0, "s-": 0, "a+": 0, "a": 0, "a-": 0, "b+": 0, "b": 0, "b-": 0, "c+": 0, "c": 0, "c-": 0, "d+": 0, "d": 0}
    data = {"total_players": 0, "counters": counters, "min_tr": min_tr}
    for player in lb["data"]["users"]:
        rank = player["league"]["rank"]
        if rank == "z":
            continue
        tr = player["league"]["rating"]
        data["total_players"]+=1
        data["counters"][rank]+=1
        if data["min_tr"][rank] > tr:
            data["min_tr"][rank] = tr
    return data


def write_data_from_buckets(data):
    if data == None:
        return
    if path.exists(THRESHOLD_FILE) and datetime.now() - datetime.fromtimestamp(path.getmtime(THRESHOLD_FILE)) < timedelta(hours=1):
        return
    relevant_data = {}
    relevant_data["date"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    relevant_data["thresholds"] = []
    for key, value in data["counters"].items():
        obj = {"rank": key, "playerCount": value, "percentage": f"{value/data['total_players']*100:.2f}", "threshold": data["min_tr"][key]}
        relevant_data["thresholds"].append(obj)
    with open(THRESHOLD_FILE, 'w') as f:
        json.dump(relevant_data, f)
        print(f"Updated @ {datetime.now()}")

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
        return True
    else:
        print(f"Ran into issues with team2xh? Status code: {resp.status_code}")
        return False

if __name__ == '__main__':
    while True:
        team2xh = download_threshold_data()
        if not team2xh:
            data = fetch_complete_leaderboard()
            buckets = sort_players_into_buckets(data)
            write_data_from_buckets(buckets)
        time.sleep(5*60)