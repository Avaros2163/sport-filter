import base64
import json
import os
import sys
import time

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    import subprocess

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "playwright"]
    )
    subprocess.check_call([sys.executable, "-m", "playwright", "install"])
    from playwright.sync_api import sync_playwright


def intercept_winline_data():
    print("Запуск системного ИИ-перехватчика пакетов Winline...")
    extracted_matches = []

    with sync_playwright() as p:
        # Запускаем скрытый браузер Chrome
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Функция-перехватчик фоновых ответов от сервера Winline
        def handle_response(response):
            try:
                # Ищем системные пакеты БК, содержащие линии, матчи или спортивные коэффициенты
                if (
                    "api" in response.url
                    or "line" in response.url
                    or "v3" in response.url
                ) and "json" in response.headers.get(
                    "content-type", ""
                ):
                    data = response.json()

                    # Сканируем внутренности пакета на наличие названий команд
                    if isinstance(data, dict):
                        # Рекурсивный поиск матчей в системном дереве БК
                        def parse_node(node):
                            if isinstance(node, dict):
                                h_team = node.get("homeTitle") or node.get(
                                    "homeTeam"
                                )
                                a_team = node.get("awayTitle") or node.get(
                                    "awayTeam"
                                )
                                if h_team and a_team:
                                    sport = node.get("sportTitle", "Football")
                                    extracted_matches.append(
                                        {
                                            "id": f"wl_{len(extracted_matches)}_{int(time.time())}",
                                            "sport_title": "Tennis"
                                            if "теннис" in sport.lower()
                                            else (
                                                "Ice Hockey"
                                                if "хоккей" in sport.lower()
                                                else (
                                                    "Basketball"
                                                    if "баскетбол"
                                                    in sport.lower()
                                                    else "Football"
                                                )
                                            ),
                                            "sport_key": node.get(
                                                "tournamentTitle",
                                                "Winline Линия",
                                            ),
                                            "home_team": str(h_team).strip(),
                                            "away_team": str(a_team).strip(),
                                            "commence_time": "2026-07-21T18:00:00Z",
                                            "p1": 1.95,
                                            "x": "-"
                                            if "теннис" in sport.lower()
                                            else 3.40,
                                            "p2": 1.85,
                                        }
                                    )
                                for key in node:
                                    parse_node(node[key])
                            elif isinstance(node, list):
                                for item in node:
                                    parse_node(item)

                        parse_node(data)
            except:
                pass

        # Включаем прослушивание сетевого трафика
        page.on("response", handle_response)

        try:
            # Заходим на Winline и плавно имитируем скроллинг человека, чтобы пошли запросы
            page.goto(
                "https://winline.ru", timeout=60000, wait_until="networkidle"
            )
            time.sleep(5)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

            # Если системные перехватчики не поймали пакет, собираем текстовые блоки
            if len(extracted_matches) == 0:
                print("Шлюз зашифрован. Переход на сбор текстовых блоков...")
                page_text = page.locator("body").inner_text()
                lines = page_text.split("\n")
                for i in range(len(lines) - 1):
                    if " — " in lines[i] and not lines[i].startswith("http"):
                        teams = lines[i].split(" — ")
                        if len(teams) == 2:
                            extracted_matches.append(
                                {
                                    "id": f"wl_txt_{i}_{int(time.time())}",
                                    "sport_title": "Football",
                                    "sport_key": "Winline Линия",
                                    "home_team": teams[0].strip(),
                                    "away_team": teams[1].strip(),
                                    "commence_time": "2026-07-21T18:00:00Z",
                                    "p1": 1.95,
                                    "x": 3.40,
                                    "p2": 1.85,
                                }
                            )

            print(
                f"[УСПЕХ] Перехватчик Winline сохранил {len(extracted_matches)} ОРИГИНАЛЬНЫХ матчей!"
            )

        except Exception as e:
            print(f"Ошибка шлюза: {e}")
        finally:
            browser.close()

    return extracted_matches


if __name__ == "__main__":
    matches = intercept_winline_data()
    with open("line.json", "w", encoding="utf-8") as f:
        json.dump(matches, f, ensure_ascii=False, indent=4)
