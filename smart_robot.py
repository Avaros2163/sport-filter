import json
import random
import time
import urllib.request

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

def fetch_sports_line():
    print("Запуск сбора спортивных матчей на сервере...")
    url = "https://jsdelivr.net"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': random.choice(USER_AGENTS)})
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = json.loads(response.read().decode('utf-8'))
            
        matches_list = []
        if isinstance(raw_data, list):
            for index, item in enumerate(raw_data):
                p1 = float(item.get("p1", 1.95))
                p2 = float(item.get("p2", 1.85))
                x = item.get("x", "-")
                x_val = float(x) if x != "-" else "-"

                matches_list.append({
                    "id": item.get("id", f"match_{index}_{int(time.time())}"),
                    "sport_title": item.get("sport_title", "Football"),
                    "sport_key": item.get("sport_key", "World Cup"),
                    "home_team": item.get("home_team", "Команда 1"),
                    "away_team": item.get("away_team", "Команда 2"),
                    "commence_time": item.get("commence_time", "2026-07-20T18:00:00Z"),
                    "p1": p1, "x": x_val, "p2": p2
                })
        if len(matches_list) > 0:
            return matches_list
    except Exception as e:
        print(f"Ошибка загрузки фида: {e}")

    # Резервный пакет, если фид недоступен
    return [
        {"id": "ai_1", "sport_title": "Football", "sport_key": "Премьер-Лига", "home_team": "Зенит", "away_team": "Спартак", "commence_time": "2026-07-20T17:30:00Z", "p1": 2.10, "x": 3.40, "p2": 3.20},
        {"id": "ai_2", "sport_title": "Ice Hockey", "sport_key": "КХЛ", "home_team": "ЦСКА", "away_team": "СКА", "commence_time": "2026-07-20T16:00:00Z", "p1": 2.25, "x": 4.10, "p2": 2.50},
        {"id": "ai_3", "sport_title": "Basketball", "sport_key": "NBA", "home_team": "Лейкерс", "away_team": "Бостон", "commence_time": "2026-07-21T02:00:00Z", "p1": 1.85, "x": "-", "p2": 1.95},
        {"id": "ai_4", "sport_title": "Tennis", "sport_key": "ATP", "home_team": "Медведев", "away_team": "Алькарас", "commence_time": "2026-07-21T14:00:00Z", "p1": 2.40, "x": "-", "p2": 1.55}
    ]

if __name__ == "__main__":
    matches = fetch_sports_line()
    with open("line.json", "w", encoding="utf-8") as f:
        json.dump(matches, f, ensure_ascii=False, indent=4)
    print(f"Файл line.json успешно обновлен на сервере. Всего матчей: {len(matches)}")
