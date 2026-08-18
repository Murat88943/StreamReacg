import json
from curl_cffi import requests
import os
import re
import time

script_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(script_dir, "config.json"), "r", encoding="utf-8") as file:
    headers = json.load(file)

base_url = "https://web.kick.com/api/v1/livestreams?limit=24&sort=viewer_count_desc&category_id=28"

cursor = ""
page = 1
all_streamers = []
seen_usernames = set()

print("сбор стримеров...")

while True:
    if cursor:
        url = f"{base_url}&after={cursor}"
    else:
        url = base_url

    try:
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)
        if response.status_code != 200:
            print(f"ошибка: статус {response.status_code}")
            break
        data = response.json()
    except Exception as e:
        print(f"ошибка запроса: {e}")
        break

    livestreams = data.get("data", {}).get("livestreams", [])

    for stream in livestreams:
        channel = stream.get("channel", {})
        username = channel.get("slug") or channel.get("username", "Неизвестно")
        viewer_count = stream.get("viewer_count", 0)

        if viewer_count < 1000:
            if username not in seen_usernames and username != "Неизвестно":
                seen_usernames.add(username)
                all_streamers.append({"username": username, "viewer_count": viewer_count})

    pagination = data.get("data", {}).get("pagination", {})
    cursor = pagination.get("next_cursor")

    if not cursor:
        break

    page += 1

output_path = os.path.join(script_dir, "data", "data.json")
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_streamers, f, ensure_ascii=False, indent=2)

print(f"собрано стримеров: {len(all_streamers)}")

print("парсинг контактов...")
contacts = {}

for streamer in all_streamers:
    username = streamer['username']
    url_contact = f"https://kick.com/{username}/about"

    try:
        response = requests.get(url_contact, headers=headers, impersonate="chrome110", timeout=30)
        html = response.text

        social_links = {"tiktok": None, "instagram": None, "twitter": None, "youtube": None, "twitch": None, "telegram": None}

        patterns = {
            "tiktok": r'https?://(?:www\.)?tiktok\.com/[^\s"\'<>]+',
            "instagram": r'https?://(?:www\.)?instagram\.com/[^\s"\'<>]+',
            "twitter": r'https?://(?:www\.)?(?:twitter|x)\.com/[^\s"\'<>]+',
            "youtube": r'https?://(?:www\.)?(?:youtube\.com|youtu\.be)/[^\s"\'<>]+',
            "twitch": r'https?://(?:www\.)?twitch\.tv/[^\s"\'<>]+',
            "telegram": r'https?://(?:t\.me|telegram\.me)/[^\s"\'<>]+'
        }

        for social, pattern in patterns.items():
            match = re.search(pattern, html)
            if match and "kick" not in match.group().lower():
                social_links[social] = match.group()

        contacts[username] = social_links
        print(f"обработан: {username}")
        time.sleep(0.5)

    except Exception as e:
        print(f"ошибка при обработке {username}: {e}")
        contacts[username] = {key: None for key in social_links}

contact_path = os.path.join(script_dir, "data", "contacts.json")
with open(contact_path, "w", encoding="utf-8") as f:
    json.dump(contacts, f, ensure_ascii=False, indent=2)

print(f"контакты сохранены в {contact_path}")

print("\nстатистика контактов:")
stats = {key: 0 for key in contacts[next(iter(contacts))] if contacts[next(iter(contacts))] is not None}
stats = {key: 0 for key in ["tiktok", "instagram", "twitter", "youtube", "twitch", "telegram"]}

for username, links in contacts.items():
    for social, link in links.items():
        if link:
            stats[social] += 1

for social, count in stats.items():
    print(f"  {social}: {count}")