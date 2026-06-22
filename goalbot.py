import requests
import os

# These grab the secrets from GitHub secretly
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
API_KEY = os.environ.get("API_KEY")

# 39 = Premier League, 140 = La Liga. Add more if you want.
LEAGUE_IDS = [39, 140] 
headers = { "x-apisports-key": API_KEY }

def send_discord_webhook(home, away, minute, scorer, detail, assist):
    goal_emoji = "⚽"
    if detail == "Own Goal": goal_emoji = "🔴"
    elif detail == "Penalty": goal_emoji = "🎯"

    embed = {
        "title": f"{goal_emoji} GOAL!",
        "color": 0x00FF00,
        "fields": [
            {"name": "Match", "value": f"**{home}** vs **{away}**", "inline": False},
            {"name": "Scorer", "value": f"**{scorer}** ({detail})", "inline": True},
            {"name": "Minute", "value": f"{minute}'", "inline": True}
        ]
    }
    if assist:
        embed["fields"].append({"name": "Assist", "value": assist, "inline": False})
    
    requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=5)

def main():
    league_str = ",".join(map(str, LEAGUE_IDS))
    url = f"https://v3.football.api-sports.io/fixtures?live=all&league={league_str}"
    
    response = requests.get(url, headers=headers, timeout=10)
    data = response.json()

    for match in data.get("response", []):
        fixture_id = match["fixture"]["id"]
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]

        events_res = requests.get(f"https://v3.football.api-sports.io/fixtures/events?fixture={fixture_id}", headers=headers, timeout=10)
        events = events_res.json().get("response", [])

        for event in events:
            if event["type"] == "Goal" and event["detail"] != "Penalty Shootout":
                # Using a simple set per run since GitHub restarts the bot every 5 mins
                minute = event["time"]["elapsed"]
                scorer = event["player"]["name"]
                detail = event["detail"]
                assist = event.get("assist", {}).get("name")
                
                print(f"Sending goal: {scorer} ({minute}')")
                send_discord_webhook(home, away, minute, scorer, detail, assist)

if __name__ == "__main__":
    main()
