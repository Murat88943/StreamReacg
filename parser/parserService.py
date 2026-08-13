import json
from curl_cffi import requests
import os

#прокси конфиги и тд
with open("config.json", "r", encoding="utf-8") as file:
    headers = json.load(file)

proxy = {
    "http": "http:// 159.112.235.190:80",
    "https": "http:// 159.112.235.190:80"
}

base_url = "https://web.kick.com/api/v1/livestreams?limit=24&sort=viewer_count_desc&category_id=28"

cursor = ""
page = 1
all_streamers = []
seen_usernames = set()

#парсер стримеров до 1к
while True:
    if cursor:
        url = f"{base_url}&after={cursor}"
    else:
        url = base_url

    response = requests.get(
        url,
        headers=headers,
        proxies=proxy,
        impersonate="chrome110"
    )

    data = response.json()

    livestreams = data.get("data", {}).get("livestreams", [])

    for stream in livestreams:
        channel = stream.get("channel", {})
        username = channel.get("username", "Неизвестно")
        viewer_count = stream.get("viewer_count", 0)

        if viewer_count < 1000:
            if username not in seen_usernames:
                seen_usernames.add(username)
                streamer_data = {
                    "username": username,
                    "viewer_count": viewer_count
                }
                all_streamers.append(streamer_data)

    pagination = data.get("data", {}).get("pagination", {})
    cursor = pagination.get("next_cursor")

    if not cursor:
        break

    page += 1


script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "data", "data.json")
os.makedirs(os.path.dirname(output_path), exist_ok=True)


with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_streamers, f, ensure_ascii=False, indent=2)


#парсер контактов
with open(output_path, 'r', encoding='utf-8') as f:
    streamers = json.load(f)

for streamer in streamers:
    username = streamer['username']
    url_contact = f"https://kick.com/{username}/about"
    print(url_contact)
