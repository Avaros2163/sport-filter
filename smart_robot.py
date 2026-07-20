import json
import random
import time
import urllib.request


def fetch_dynamic_sports_line():
    print("Запуск сбора спортивных маркетов через поисковый шлюз...")

    # Подключаемся к базе категорий, чтобы забрать структуру спортивных событий
    url = "https://wikipedia.org"

    matches_list = []
    current_timestamp = int(time.time())

    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = json.loads(response.read().decode("utf-8"))

        # Извлекаем чистые динамические данные из базы
        pages = raw_data.get("query", {}).get("categorymembers", [])

        if len(pages) > 1:
            # Разбиваем полученный список на пары случайным образом для создания матчей
            for i in range(0, len(pages) - 1, 2):
                home = pages[i].get("title", "").replace(" (футбольный клуб)", "")
                away = (
                    pages[i + 1].get("title", "").replace(" (футбольный club)", "")
                )

                if home and away:
                    # Распределяем по разным видам спорта и лигам автоматически
                    sport_type = random.choice(
                        ["Football", "Ice Hockey", "Basketball"]
                    )
                    league_name = (
                        "Мировой Турнир"
                        if sport_type == "Football"
                        else ("КХЛ / НХЛ" if sport_type == "Ice Hockey" else "NBA")
                    )

                    matches_list.append(
                        {
                            "id": f"dyn_{i}_{current_timestamp}",
                            "sport_title": sport_type,
                            "sport_key": league_name,
                            "home_team": home,
                            "away_team": away,
                            "commence_time": f"2026-07-{21 + (i % 5)}T19:00:00Z",
                            "p1": round(random.uniform(1.50, 3.20), 2),
                            "x": "-"
                            if sport_type == "Basketball"
                            else round(random.uniform(3.10, 4.50), 2),
                            "p2": round(random.uniform(1.80, 3.50), 2),
                        }
                    )

            print(f"УСПЕХ! Робот собрал {len(matches_list)} динамических матчей!")
            return matches_list
    except Exception as e:
        print(f"Поисковый шлюз занят, активирую системный буфер: {e}")

    # Полностью обезличенный системный буфер без названий команд, если база не ответила
    for i in range(1, 11):
        matches_list.append(
            {
                "id": f"sys_{i}_{current_timestamp}",
                "sport_title": "Football",
                "sport_key": "Высшая Лига",
                "home_team": f"Состав {i}",
                "away_team": f"Состав {i+10}",
                "commence_time": "2026-07-22T18:00:00Z",
                "p1": 2.10,
                "x": 3.40,
                "p2": 2.80,
            }
        )
    return matches_list


if __name__ == "__main__":
    matches = fetch_dynamic_sports_line()
    with open("line.json", "w", encoding="utf-8") as f:
        json.dump(matches, f, ensure_ascii=False, indent=4)
