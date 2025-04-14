# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.expanduser("~/.local/lib/python3.10/site-packages"))
import subprocess
import datetime
import pytz
import time
from googlesearch import search
import snscrape
from datetime import datetime, timedelta  # Додано імпорт timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append(os.path.expanduser("~/.local/lib/python3.10/site-packages"))

# Ключові слова
KEYWORDS = [
    "Т0710",
    "Державна спеціальна служба транспорту"
]

LOG_FILE = "log.txt"
EMAIL_TO = "romanskinner1996@gmail.com"
EMAIL_FROM = "romanskinner1996@gmail.com"
EMAIL_PASS = "mtafypgmszwgljnp"

# Завантажити вже знайдені посилання
def load_logged_links():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

# Додати нові посилання до логів
def save_logged_links(links):
    with open(LOG_FILE, "a") as f:
        for link in links:
            f.write(link + "\n")

# Відправити email з HTML-контентом
def send_email(content_html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Моніторинг згадок (оновлення)"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    html_part = MIMEText(content_html, "html", "utf-8")
    msg.attach(html_part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASS)
            server.send_message(msg)
    except Exception as e:
        print(f"Помилка при надсиланні email: {e}")

# Пошук у Google
def search_google(keyword):
    query = keyword
    results = list(search(query, num_results=10))
    return results

# Пошук Facebook через Google site:facebook.com
def search_facebook(keyword):
    query = f"site:facebook.com {keyword}"
    results = list(search(query, num_results=10))
    return results

# Пошук Telegram через Google site:t.me
def search_telegram(keyword):
    query = f"site:t.me {keyword}"
    results = list(search(query, num_results=10))
    return results

# Пошук у Twitter за останні 2 години
def search_twitter(keyword):
    since_time = (datetime.utcnow() - timedelta(hours=2)).isoformat(timespec="seconds")
    try:
        command = ["snscrape", "twitter-search", f"{keyword} since:{since_time}"]
        output = subprocess.check_output(command, stderr=subprocess.DEVNULL).decode("utf-8")
        return output if output.strip() else "Нічого не знайдено"
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            return "Нічого не знайдено"
        return f"Помилка при пошуку в Twitter: {e}"
    except Exception as e:
        return f"Помилка при пошуку в Twitter: {e}"

# Основна логіка моніторингу
def monitor():
    print("Функція моніторингу викликана")  # Додаємо виведення в консоль для перевірки
    kyiv_tz = pytz.timezone("Europe/Kyiv")
    now = datetime.now(kyiv_tz).strftime("%Y-%m-%d %H:%M")
    print(f"\n=== Моніторинг на {now} ===\n")
    logged_links = load_logged_links()
    new_links = set()
    html = f"""
    <html>
    <body style='font-family:sans-serif;'>
    <h2>Моніторинг на {now}</h2>
    """

    for keyword in KEYWORDS:
        html += f"<h3>{keyword}</h3>"

        google_results = search_google(keyword)
        google_filtered = [url for url in google_results if url not in logged_links]
        new_links.update(google_filtered)
        html += "<b>Google:</b><ul>"
        for url in google_filtered:
            html += f"<li><a href='{url}'>{url}</a></li>"
        html += "</ul>"

        fb_results = search_facebook(keyword)
        fb_filtered = [url for url in fb_results if url not in logged_links]
        new_links.update(fb_filtered)
        html += "<b>Facebook:</b><ul>"
        for url in fb_filtered:
            html += f"<li><a href='{url}'>{url}</a></li>"
        html += "</ul>"

        tg_results = search_telegram(keyword)
        tg_filtered = [url for url in tg_results if url not in logged_links]
        new_links.update(tg_filtered)
        html += "<b>Telegram:</b><ul>"
        for url in tg_filtered:
            html += f"<li><a href='{url}'>{url}</a></li>"
        html += "</ul>"

        twitter_result = search_twitter(keyword).replace("\n", "<br>")
        html += f"<b>Twitter:</b><div style='margin-bottom:20px;'>{twitter_result}</div>"

    html += "</body></html>"

    if new_links:
        save_logged_links(new_links)
        send_email(html)
    else:
        print("Нових згадок немає.")

# Нескінченний запуск кожні 2 години
if __name__ == "__main__":
    while True:
        monitor()
        time.sleep(7200)  # Чекає 2 години
