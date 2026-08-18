import json
import os
import time
import random
from playwright.sync_api import sync_playwright

script_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(script_dir, "data", "contacts.json"), "r", encoding="utf-8") as f:
    contacts = json.load(f)

with open(os.path.join(os.path.dirname(script_dir), "mailers", "templates.json"), "r", encoding="utf-8") as f:
    data = json.load(f)
    letter_templates = data if isinstance(data, list) else data.get("letters", [])

try:
    from data.data_auth import instagram_login, instagram_password, discord_login, discord_password, twitter_login, \
        twitter_password, tiktok_login, tiktok_password
except ImportError:
    instagram_login = instagram_password = discord_login = discord_password = twitter_login = twitter_password = tiktok_login = tiktok_password = ""


class SocialSender:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    def start(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context(viewport={'width': 1280, 'height': 720})

    def stop(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def send_instagram(self, profile_url, message):
        try:
            if not profile_url:
                return False
            username = profile_url.split("/")[-1] or profile_url.split(".com/")[-1].split("/")[0]
            print(f"  instagram @{username}")
            page = self.context.new_page()
            page.goto("https://www.instagram.com/accounts/login/")
            time.sleep(3)
            page.fill('input[name="username"]', instagram_login)
            page.fill('input[name="password"]', instagram_password)
            page.click('button[type="submit"]')
            time.sleep(5)
            page.goto(f"https://www.instagram.com/{username}/")
            time.sleep(3)
            for selector in ['button:has-text("Сообщение")', 'button:has-text("Message")']:
                btn = page.locator(selector)
                if btn.count() > 0:
                    btn.click()
                    time.sleep(2)
                    textarea = page.locator('textarea[placeholder*="Сообщение"], textarea[placeholder*="Message"]')
                    if textarea.count() > 0:
                        textarea.fill(message[:1000])
                        time.sleep(1)
                        send = page.locator('button:has-text("Отправить"), button:has-text("Send")')
                        if send.count() > 0:
                            send.click()
                            time.sleep(2)
                            page.close()
                            return True
            page.close()
            return False
        except:
            return False

    def send_twitter(self, profile_url, message):
        try:
            if not profile_url:
                return False
            username = profile_url.split("/")[-1]
            print(f"  twitter @{username}")
            page = self.context.new_page()
            page.goto("https://twitter.com/login")
            time.sleep(3)
            page.fill('input[autocomplete="username"]', twitter_login)
            page.click('button:has-text("Next")')
            time.sleep(2)
            page.fill('input[name="password"]', twitter_password)
            page.click('button:has-text("Log in")')
            time.sleep(5)
            page.goto(f"https://twitter.com/{username}")
            time.sleep(3)
            btn = page.locator('a[aria-label*="Message"], a[aria-label*="Сообщение"]')
            if btn.count() > 0:
                btn.click()
                time.sleep(2)
                textarea = page.locator('div[data-testid="dmComposerInput"]')
                if textarea.count() > 0:
                    textarea.fill(message[:280])
                    time.sleep(1)
                    send = page.locator('button[data-testid="dmSendButton"]')
                    if send.count() > 0:
                        send.click()
                        time.sleep(2)
                        page.close()
                        return True
            page.close()
            return False
        except:
            return False

    def send_tiktok(self, profile_url, message):
        try:
            if not profile_url:
                return False
            username = profile_url.split("/")[-1].replace("@", "")
            print(f"  tiktok @{username}")
            page = self.context.new_page()
            page.goto("https://www.tiktok.com/login")
            time.sleep(3)
            page.click('div[data-e2e="login-enter-email"]')
            time.sleep(1)
            page.fill('input[placeholder*="Email"]', tiktok_login)
            page.fill('input[placeholder*="Password"]', tiktok_password)
            page.click('button[data-e2e="login-submit"]')
            time.sleep(5)
            page.goto(f"https://www.tiktok.com/@{username}")
            time.sleep(3)
            btn = page.locator('button:has-text("Message"), button:has-text("Сообщение")')
            if btn.count() > 0:
                btn.click()
                time.sleep(2)
                textarea = page.locator('textarea[placeholder*="Message"], textarea[placeholder*="Сообщение"]')
                if textarea.count() > 0:
                    textarea.fill(message[:300])
                    time.sleep(1)
                    send = page.locator('button:has-text("Send"), button:has-text("Отправить")')
                    if send.count() > 0:
                        send.click()
                        time.sleep(2)
                        page.close()
                        return True
            page.close()
            return False
        except:
            return False

    def send_discord(self, webhook_url, message):
        try:
            if not webhook_url:
                return False
            print("  discord")
            page = self.context.new_page()
            page.goto("https://discord.com/login")
            time.sleep(3)
            page.fill('input[name="email"]', discord_login)
            page.fill('input[name="password"]', discord_password)
            page.click('button[type="submit"]')
            time.sleep(5)
            page.goto(webhook_url)
            time.sleep(3)
            textarea = page.locator('textarea[placeholder*="Сообщение"], textarea[placeholder*="Message"]')
            if textarea.count() > 0:
                textarea.fill(message[:2000])
                time.sleep(1)
                page.click('button:has-text("Отправить"), button:has-text("Send")')
                time.sleep(2)
                page.close()
                return True
            page.close()
            return False
        except:
            return False


def main():
    print("\n" + "=" * 50)
    print("РАССЫЛКА")
    print("=" * 50)
    print(f"стримеров: {len(contacts)}")
    print(f"шаблонов: {len(letter_templates)}")
    print("=" * 50)

    sender = SocialSender()
    sender.start()

    sent = 0
    success = 0

    try:
        for username, links in contacts.items():
            template = random.choice(letter_templates) if letter_templates else {"subject": "", "body": ""}
            body = template.get("body", "").replace("{streamer_name}", username).replace("{manager_name}",
                                                                                         "Алексей").replace(
                "{casino_name}", "Lucky Star")
            msg = f"{template.get('subject', '')}\n\n{body}" if template.get("subject") else body

            available = [s for s, l in links.items() if l]
            if not available:
                continue

            print(f"\n{username}: {', '.join(available)}")

            ok = False
            for social, url in links.items():
                if not url:
                    continue
                if social == "instagram" and sender.send_instagram(url, msg):
                    success += 1
                    ok = True
                    time.sleep(3)
                elif social == "twitter" and sender.send_twitter(url, msg):
                    success += 1
                    ok = True
                    time.sleep(3)
                elif social == "tiktok" and sender.send_tiktok(url, msg):
                    success += 1
                    ok = True
                    time.sleep(3)
                elif social == "discord" and sender.send_discord(url, msg):
                    success += 1
                    ok = True
                    time.sleep(3)

            if ok:
                sent += 1
                delay = random.randint(10, 30)
                print(f"пауза {delay}с")
                time.sleep(delay)

    except KeyboardInterrupt:
        print("\nстоп")
    finally:
        sender.stop()

    print(f"обработано: {sent}")
    print(f"отправлено: {success}")
    print("=" * 50)


if __name__ == "__main__":
    main()