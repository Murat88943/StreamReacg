import json
import os
import re
import time
from curl_cffi import requests

data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

headers = {
    "user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/120.0.0.0 safari/537.36",
    "accept": "application/json",
    "referer": "https://kick.com/"
}

base_url = "https://web.kick.com/api/v1/livestreams?limit=24&sort=viewer_count_desc&category_id=28"

all_streamers = []
seen_usernames = set()
cursor = None

while True:
    url = base_url
    if cursor:
        url = f"{base_url}&after={cursor}"

    try:
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=30)
        if response.status_code != 200:
            break
        data = response.json()
    except:
        break

    payload = data.get("data") or {}
    livestreams = payload.get("livestreams") or []

    if not livestreams:
        break

    for stream in livestreams:
        if not isinstance(stream, dict):
            continue
        channel = stream.get("channel") or {}
        username = channel.get("slug") or channel.get("username") or ""
        username = str(username).strip()
        if not username:
            continue
        try:
            viewer_count = int(stream.get("viewer_count") or 0)
        except:
            viewer_count = 0
        if viewer_count >= 1000:
            continue
        key = username.lower()
        if key in seen_usernames:
            continue
        seen_usernames.add(key)
        all_streamers.append({"username": username, "viewer_count": viewer_count})

    pagination = payload.get("pagination") or {}
    next_cursor = pagination.get("next_cursor")
    if not next_cursor or next_cursor == cursor:
        break
    cursor = next_cursor
    time.sleep(0.5)

data_path = os.path.join(data_dir, "data.json")
with open(data_path, "w", encoding="utf-8") as f:
    json.dump(all_streamers, f, ensure_ascii=False, indent=2)

contacts = {}

social_patterns = {
    "instagram": r'https?://(?:www\.)?instagram\.com/[a-zA-Z0-9._-]+/?',
    "twitter": r'https?://(?:www\.)?(?:twitter|x)\.com/[a-zA-Z0-9._-]+/?',
    "tiktok": r'https?://(?:www\.)?tiktok\.com/@?[a-zA-Z0-9._-]+/?'
}

def extract_social_links(html):
    social_links = {"instagram": None, "twitter": None, "tiktok": None}
    for social, pattern in social_patterns.items():
        matches = re.findall(pattern, html, re.IGNORECASE)
        for link in matches:
            link = link.rstrip(".,);]}>\"'/")
            if "kick" not in link.lower():
                social_links[social] = link
                break
    return social_links

for streamer in all_streamers:
    username = streamer["username"]
    about_url = f"https://kick.com/{username}/about"

    try:
        response = requests.get(about_url, headers=headers, impersonate="chrome110", timeout=30)
        if response.status_code != 200:
            contacts[username] = {"instagram": None, "twitter": None, "tiktok": None}
            continue

        html = response.text
        social_links = extract_social_links(html)
        contacts[username] = social_links
        time.sleep(0.3)

    except:
        contacts[username] = {"instagram": None, "twitter": None, "tiktok": None}

contacts_path = os.path.join(data_dir, "contacts.json")
with open(contacts_path, "w", encoding="utf-8") as f:
    json.dump(contacts, f, ensure_ascii=False, indent=2)
