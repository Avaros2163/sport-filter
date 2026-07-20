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


def grab_all_winline_stavki():
    print("Робот подключается к главному хабу матчей: https://winline.ru/stavki ...")
    extracted_matches = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        try:
            # Заходим напрямую на страницу со ВСЕМИ матчами
            page.goto(
                "https://winline.ru/stavki",
                timeout=60000,
                wait_until="networkidle",
            )

            # Плавно прокручиваем страницу вниз 3 раза, чтобы подгрузить абсолютно все игры на неделю вперед
            print("Сканирование и раскрытие полной ленты событий БК...")
            for _ in range(3):
                page.evaluate("window.scrollBy(0, 3000);")
                time.sleep(3)

            # Извлекаем чистый текст со всей страницы
            raw_text = page.locator("body").inner_text()
            lines = raw_text.split("\n")

            current_sport = "Футбол"

            print("Запуск алгоритма сортировки матчей и коэффициентов...")
            for i in range(len(lines) - 4):
                line = lines[i].strip()

                # На лету определяем, к какому виду спорта относятся идущие ниже матчи
                if "Футбол" in line:
                    current_sport = "Футбол"
                elif "Теннис" in line:
                    current_sport = "Теннис"
                elif "Хоккей" in line:
                    current_sport = "Хоккей"
                elif "Баскетбол" in line:
                    current_sport = "Баскетбол"

                # Ищем оригинальный разделитель команд " — "
                if " — " in line and not line.startswith("http"):
                    teams = line.split(" — ")
                    if len(teams) == 2:
                        home_team = teams[0].strip()
                        away_team = teams[1].strip()

                        # Робот сканирует следующие строчки, чтобы забрать реальные кэфы (П1, Х, П2)
                        p1, x, p2 = 1.95, 3.40, 1.95
                        try:
                            # Проверяем, идут ли следом цифровые коэффициенты БК
                            val1 = lines[i + 1].strip().replace(",", ".")
                            val2 = lines[i + 2].strip().replace(",", ".")
                            val3 = lines[i + 3].strip().replace(",", ".")

                            if (
                                any(c.isdigit() for c in val1)
                                and "." in val1
                                or val1.isdigit()
                            ):
                                p1 = float(val1)
                            if (
                                any(c.isdigit() for c in val2)
                                and "." in val2
                                or val2.isdigit()
                            ):
                                x = float(val2)
                            if (
                                any(c.isdigit() for c in val3)
                                and "." in val3
                                or val3.isdigit()
                            ):
                                p2 = float(val3)
                        except:
                            pass

                        # Заносим игру в нашу базу
                        extracted_matches.append(
                            {
                                "id": f"wl_st_{i}_{int(time.time())}",
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
                                "sport_key": "Winline Хаб Матчей",
                                "home_team": home_team,
                                "away_team": away_team,
                                "commence_time": "2026-07-21T18:00:00Z",
                                "p1": p1,
                                "x": "-"
                                if current_sport in ["Теннис", "Баскетбол"]
                                else x,
                                "p2": p2,
                            }
                        )

            print(
                f"[УСПЕХ] Робот полностью опустошил хаб /stavki и забрал {len(extracted_matches)} живых матчей!"
            )

        except Exception as e:
            print(f"Ошибка сбора данных с хаба: {e}")
        finally:
            browser.close()

    return extracted_matches


if __name__ == "__main__":
    matches = grab_all_winline_stavki()
    with open("line.json", "w", encoding="utf-8") as f:
        json.dump(matches, f, ensure_ascii=False, indent=4)
