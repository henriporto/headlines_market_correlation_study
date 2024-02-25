import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta

DB = "headlines.db"


def create_table():
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS headlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                headline TEXT, 
                ydm DATE,
                output TEXT
            )
        """
        )


def insert_data(headlines, date):
    print(date)
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO headlines (headline, ydm) VALUES (?, ?)",
            [(headline, date) for headline in headlines],
        )


def fetch_headlines(session, year, month, day):
    url = f"https://www.wsj.com/news/archive/{year}/{month}/{day}?page="
    page_num = 1
    headlines = []
    while True:
        response = session.get(url + str(page_num))
        if response.status_code == 404:
            break
        soup = BeautifulSoup(response.text, "html.parser")
        page_headlines = [
            headline.get_text()
            for headline in soup.find_all(
                "span", {"class": lambda x: x and "WSJTheme--headlineText" in x}
            )
        ]
        if not page_headlines:
            break
        headlines.extend(page_headlines)
        page_num += 1
    return headlines


def main():
    headers = {
        "authority": "www.wsj.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "max-age=0",
        "cookie": "",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
    session = requests.Session()
    session.headers.update(headers)
    create_table()
    start_date = datetime(1998, 1, 1)
    end_date = datetime(2023, 12, 31)
    current_date = start_date
    while current_date <= end_date:
        headlines = fetch_headlines(
            session, current_date.year, current_date.month, current_date.day
        )
        insert_data(headlines, current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)


if __name__ == "__main__":
    main()
