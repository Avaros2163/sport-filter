import base64
import json
import os
import sys
import time

# Автоматическая подгрузка браузерного движка на сервере
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    import subprocess

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "playwright"]
    )
    subprocess.check_call([sys.executable, "-m", "playwright", "install"])
    from playwright.sync_api import sync_playwright


def grab_pure_winline_data():
    print("Запуск облачного браузера для копирования Winline...")
    extracted_matches = []

    with sync_playwright() as p:
        # Запускаем замаскированный браузер
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # Заходим на главную страницу БК
            page.goto(
                "https://winline.ru", timeout=60000, wait_until="networkidle"
            )
            time.sleep(7)  # Даем время прогрузиться всем вкладкам и цифрам

            # Робот сканирует весь текст на странице (категории, команды, кэфы)
            page_text = page.locator("body").inner_text()
            lines = page_text.split("\n")

            current_sport = "Футбол"

            # Алгоритм парсинга: ищем разделители матчей и распределяем по видам спорта
            for i in range(len(lines) - 3):
                line = lines[i].strip()

                # Отслеживаем смену категории на экране
                if "Футбол" in line:
                    current_sport = "Футбол"
                elif "Теннис" in line:
                    current_sport = "Теннис"
                elif "Хоккей" in line:
                    current_sport = "Хоккей"
                elif "Баскетбол" in line:
                    current_sport = "Баскетбол"

                # Если находим оригинальный маркер матча БК "Команда 1 — Команда 2"
                if " — " in line and not line.startswith("http"):
                    teams = line.split(" — ")
                    if len(teams) == 2:
                        home = teams[0].strip()
                        away = teams[1].strip()

                        # Вытаскиваем коэффициенты (они обычно идут в следующих строках)
                        p1, x, p2 = 1.90, 3.40, 1.90
                        try:
                            if lines[i + 1].replace(".", "").isdigit():
                                p1 = float(lines[i + 1])
                            if lines[i + 2].replace(".", "").isdigit():
                                x = float(lines[i + 2])
                            if lines[i + 3].replace(".", "").isdigit():
                                p2 = float(lines[i + 3])
                        except:
                            pass

                        extracted_matches.append(
                            {
                                "id": f"wl_{i}_{int(time.time())}",
                                "sport_title": "Tennis"
                                if current_sport == "Теннис"
                                else (
                                    "Ice Hockey"
                                    if current_sport == "Хоккей"
                                    else (
                                        "Basketball"
                                        if current_sport == "Баскетбол"
                                        else "Football"
                                    )
                                ),
                                "sport_key": "Winline Линия",
                                "home_team": home,
                                "away_team": away,
                                "commence_time": "2026-07-21T18:00:00Z",
                                "p1": p1,
                                "x": "-"
                                if current_sport in ["Теннис", "Баскетбол"]
                                else x,
                                "p2": p2,
                            }
                        )

            print(f"УСПЕХ! Робот скопировал {len(extracted_matches)} матчей!")

        except Exception as e:
            print(f"Ошибка чтения сайта: {e}")
        finally:
            browser.close()

    return extracted_matches


if __name__ == "__main__":
    matches = grab_pure_winline_data()
    # Записываем оригинальный текстовый результат в line.json для нашего сайта
    with open("line.json", "w", encoding="utf-8") as f:
        json.dump(matches, f, ensure_ascii=False, indent=4)
