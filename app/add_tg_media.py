import json

import bs4
import requests
from requests import JSONDecodeError
from loguru import logger
from tqdm.auto import tqdm

payload = {}
headers = {
    "authority": "telegramchannels.me",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en",
    "cache-control": "max-age=0",
    "cookie": (
        "XSRF-TOKEN=eyJpdiI6ImszS1hYeFBTeFBFRUNnWXlETHlPWVE9PSIsInZhbHVlIjoid09aUlFYcitRYUpiWmZycWRQL0dTWUNUamowMlNHRTk0N1pHMU1IRm1aWmZIYzB1RHNhelRhVHJhZlp0MWRmdlVWMXk4NGJkUkRNaDNBVXpJTkRtd1AwUUFhQ1ZtaGNIdTRsaXphS2tmSGdScHkwQzBzNnUrUVdQeUg3b2Fya2UiLCJtYWMiOiI5Y2Q0MzliZTA3MDRlNzhiNjIwNTNmMjJhZjQzMDdmYmQ0ZWVkODk3Mjk1OWJjOGU1MGI3Yzg2MzY4MDE3NzA5In0%3D;"
        " telegram_channels_session=eyJpdiI6ImhyZlA4Uml2by9GV2JlT0FETHZiVmc9PSIsInZhbHVlIjoiU0paeHlYdUY4a01aYUZuOERKcHVYSW44VVhOV3ZSZlc4WlRsZ2JlS3VBUXJ4MHVKN1FSM2paMWxEQ0djSk4rUjQyeFdwLysyd2JEV1FYTXh2dFpUK3drNmdNdVFuUm1JUC9RUWpya3BRYm85WWI0TWdUeWo3RXZNRFpiKy9TTTMiLCJtYWMiOiIyNzYxNGQxYmYxMmYzYTQ5MDFiYjUxYTViYzkxMmQyODU4ODA0YzUxMjA4OTU5ZjY4M2VjOGZmZTM5YzkzNmY1In0%3D;"
        " XSRF-TOKEN=eyJpdiI6IkErMVM4TnM1V2lRVjNYbVNydmQ2M0E9PSIsInZhbHVlIjoiRnlOU2FWeHlpUkZ6UllWcjg0bzdMUFFFUnlrYVArV1hMWWY3VGErdmc0M1hLa3MvWGY0VTFnRUZiLzhPTHdZTUxwMUs4Sk9Hd0FUekdHZG1LTkRDekNBUE9Zemc2S1ZsRFVzdi9WZ3JKcmozQm5SVzBLVE1YMFJsMk82YXEzQ2wiLCJtYWMiOiJkYmMwYzI3YWFlOGI3Y2VhY2ZkMzZjOWVjOTEwYjZlZGNlYzUyNDFiZDA5MmZlYzM3NDYzNTkyNjA3YjU2M2UwIn0%3D;"
        " telegram_channels_session=eyJpdiI6Ikk5alM3KytSMEZwVHAxL2RnZjAzYkE9PSIsInZhbHVlIjoiYzVDWVhmdzUxejVPLzlpZWU1b1NMR01mZi8zMTVQeWdyREVhYlM2ajVHMHhUKzg4MmJ2SWZkdjBsRWRjZGg4cGU2bVF3SGxJNnNHZU5NWlkyeStqNWZ3UjR6VHRTZGpmS1licG1LbWVwSWx5MVRqYUFsdXNJQU11amU4NjluZTgiLCJtYWMiOiIyODg5YzU2MmRiMGE5ZTRmZWMxNThkNDlhNGZkOTUwMzdmNzQ1MjBmMTcyNGJjMGZiZDMyNDcxNzFmOWRmNWU3In0%3D"
    ),
    "referer": "https://telegramchannels.me/stickers",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/100.0.4896.127 Safari/537.36"
    ),
}

for language in tqdm(["en", "ru"]):
    for category in tqdm(
        [
            "art-design",
            "communication",
            "news",
            "blogs",
            "books-magazine",
            "economics-politics",
            "cryptocurrencies",
            "education",
            "entertainment",
            "games-apps",
            "health",
            "music",
            "science",
            "love",
        ]
    ):
        for page_obj in ["stickers", "channels", "bots"]:
            for page in range(1, 3):
                url = f"https://telegramchannels.me/{language}/{page_obj}?category={category}&sort=rating&page={page}"
                response = requests.request(
                    "GET", url.format(page), headers=headers, data=payload
                )
                html = bs4.BeautifulSoup(response.text, "html")
                files = html.find_all(
                    "div",
                    {
                        "class": (
                            "column is-one-third-widescreen is-one-third-desktop"
                            " is-half-tablet is-full-mobile"
                        )
                    },
                )
                for file in files:
                    type_obj, _ = (
                        file.find(attrs={"class": "card-label"})
                        .text.strip()
                        .lower()
                        .split(" / ")
                    )
                    name = file.find(
                        "a",
                        attrs={"class": "is-clickable is-block has-text-grey-darker"},
                    )["href"].split("/")[-1]
                    if type_obj in ("channel", "group", "bot") or type_obj in (
                        "канал",
                        "бот",
                        "группа",
                    ):
                        tg_url = f"https://t.me/{name}"
                    elif type_obj == "sticker" or type_obj == "стикер":
                        tg_url = f'https://t.me/addstickers/{name.split("-")[1]}'
                    else:
                        logger.warning(f"Warn! {type_obj}")
                        continue

                    resp = requests.request(
                        "POST",
                        "https://maxsecure.space/telegram/new",
                        data=json.dumps(
                            {"url": tg_url, "category": category, "language": language}
                        ),
                    )
                    try:
                        if resp.status_code not in (200, 409):
                            logger.debug(type_obj, name, resp.json())
                    except JSONDecodeError:
                        pass
