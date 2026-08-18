import json
from curl_cffi import requests
import os
import re
import time

with open("config.json", "r", encoding="utf-8") as file:
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

    response = requests.get(
        url,
        headers=headers,
        impersonate="chrome110",
        timeout=30
    )

    data = response.json()
    livestreams = data.get("data", {}).get("livestreams", [])

    for stream in livestreams:
        channel = stream.get("channel", {})
        username = channel.get("slug") or channel.get("username", "Неизвестно")
        viewer_count = stream.get("viewer_count", 0)

        if viewer_count < 1000:
            if username not in seen_usernames and username != "Неизвестно":
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

script_dir = os.getcwd()
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
        response = requests.get(
            url_contact,
            headers=headers,
            impersonate="chrome110",
            timeout=30
        )

        html = response.text

        social_links = {
            "tiktok": None,
            "instagram": None,
            "twitter": None,
            "youtube": None,
            "twitch": None,
            "telegram": None
        }

        tiktok_pattern = r'https?://(?:www\.)?tiktok\.com/[^\s"\'<>]+'
        instagram_pattern = r'https?://(?:www\.)?instagram\.com/[^\s"\'<>]+'
        twitter_pattern = r'https?://(?:www\.)?(?:twitter|x)\.com/[^\s"\'<>]+'
        youtube_pattern = r'https?://(?:www\.)?(?:youtube|youtu\.be)/[^\s"\'<>]+'
        twitch_pattern = r'https?://(?:www\.)?twitch\.tv/[^\s"\'<>]+'
        telegram_pattern = r'https?://(?:t\.me|telegram\.me)/[^\s"\'<>]+'

        tiktok_match = re.search(tiktok_pattern, html)
        instagram_match = re.search(instagram_pattern, html)
        twitter_match = re.search(twitter_pattern, html)
        youtube_match = re.search(youtube_pattern, html)
        twitch_match = re.search(twitch_pattern, html)
        telegram_match = re.search(telegram_pattern, html)

        if tiktok_match and "kick" not in tiktok_match.group().lower():
            social_links["tiktok"] = tiktok_match.group()
        if instagram_match and "kick" not in instagram_match.group().lower():
            social_links["instagram"] = instagram_match.group()
        if twitter_match and "kick" not in twitter_match.group().lower():
            social_links["twitter"] = twitter_match.group()
        if youtube_match and "kick" not in youtube_match.group().lower():
            social_links["youtube"] = youtube_match.group()
        if twitch_match and "kick" not in twitch_match.group().lower():
            social_links["twitch"] = twitch_match.group()
        if telegram_match and "kick" not in telegram_match.group().lower():
            social_links["telegram"] = telegram_match.group()

        contacts[username] = social_links

        print(f"обработан: {username}")
        time.sleep(0.5)

    except Exception as e:
        print(f"ошибка при обработке {username}: {e}")
        contacts[username] = {
            "tiktok": None,
            "instagram": None,
            "twitter": None,
            "youtube": None,
            "twitch": None,
            "telegram": None
        }

contact_path = os.path.join(script_dir, "data", "contacts.json")
with open(contact_path, "w", encoding="utf-8") as f:
    json.dump(contacts, f, ensure_ascii=False, indent=2)

print(f"контакты сохранены в {contact_path}")

print("\nстатистика контактов:")
stats = {
    "tiktok": 0,
    "instagram": 0,
    "twitter": 0,
    "youtube": 0,
    "twitch": 0,
    "telegram": 0
}

for username, links in contacts.items():
    for social, link in links.items():
        if link:
            stats[social] += 1

for social, count in stats.items():
    print(f"  {social}: {count}")