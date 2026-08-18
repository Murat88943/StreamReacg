import json
import os
import time
import random
import sys
from playwright.sync_api import sync_playwright

script_dir = os.path.dirname(os.path.abspath(__file__))
parser_dir = os.path.dirname(script_dir)

contact_path = os.path.join(parser_dir, "parser", "data", "contacts.json")
with open(contact_path, "r", encoding="utf-8") as f:
    contacts = json.load(f)

templates_path = os.path.join(script_dir, "templates.json")
with open(templates_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    letter_templates = data if isinstance(data, list) else data.get("letters", [])

auth_path = os.path.join(parser_dir, "parser", "data")
sys.path.insert(0, auth_path)

try:
    from data.data_auth import instagram_login, instagram_password, discord_login, discord_password, twitter_login, twitter_password, tiktok_login, tiktok_password
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
        if not profile_url:
            return False
        try:
            username = profile_url.rstrip("/").split("/")[-1]
            if not username:
                username = profile_url.split(".com/")[-1].split("/")[0]
            if not username:
                return False
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
                    for textarea_sel in ['textarea[placeholder*="Сообщение"]', 'textarea[placeholder*="Message"]']:
                        textarea = page.locator(textarea_sel)
                        if textarea.count() > 0:
                            textarea.fill(message[:1000])
                            time.sleep(1)
                            for send_sel in ['button:has-text("Отправить")', 'button:has-text("Send")']:
                                send = page.locator(send_sel)
                                if send.count() > 0:
                                    send.click()
                                    time.sleep(2)
                                    page.close()
                                    return True
            page.close()
            return False
        except Exception as e:
            print(f"  ошибка instagram: {e}")
            return False

    def send_twitter(self, profile_url, message):
        if not profile_url:
            return False
        try:
            username = profile_url.rstrip("/").split("/")[-1]
            if not username:
                return False
            print(f"  twitter @{username}")
            page = self.context.new_page()
            page.goto("https://twitter.com/login")
            time.sleep(3)
            for user_sel in ['input[autocomplete="username"]', 'input[name="text"]']:
                user_input = page.locator(user_sel)
                if user_input.count() > 0:
                    user_input.fill(twitter_login)
                    break
            page.click('button:has-text("Next")')
            time.sleep(2)
            page.fill('input[name="password"]', twitter_password)
            page.click('button:has-text("Log in")')
            time.sleep(5)
            page.goto(f"https://twitter.com/{username}")
            time.sleep(3)
            for btn_sel in ['a[aria-label*="Message"]', 'a[aria-label*="Сообщение"]']:
                btn = page.locator(btn_sel)
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
        except Exception as e:
            print(f"  ошибка twitter: {e}")
            return False

    def send_tiktok(self, profile_url, message):
        if not profile_url:
            return False
        try:
            username = profile_url.rstrip("/").split("/")[-1].replace("@", "")
            if not username:
                return False
            print(f"  tiktok @{username}")
            page = self.context.new_page()
            page.goto("https://www.tiktok.com/login")
            time.sleep(3)
            for login_sel in ['div[data-e2e="login-enter-email"]', 'div:has-text("Email")']:
                login_btn = page.locator(login_sel)
                if login_btn.count() > 0:
                    login_btn.click()
                    break
            time.sleep(1)
            for email_sel in ['input[placeholder*="Email"]', 'input[type="email"]']:
                email_input = page.locator(email_sel)
                if email_input.count() > 0:
                    email_input.fill(tiktok_login)
                    break
            for pass_sel in ['input[placeholder*="Password"]', 'input[type="password"]']:
                pass_input = page.locator(pass_sel)
                if pass_input.count() > 0:
                    pass_input.fill(tiktok_password)
                    break
            for sub_sel in ['button[data-e2e="login-submit"]', 'button:has-text("Log in")']:
                submit = page.locator(sub_sel)
                if submit.count() > 0:
                    submit.click()
                    break
            time.sleep(5)
            page.goto(f"https://www.tiktok.com/@{username}")
            time.sleep(3)
            for btn_sel in ['button:has-text("Message")', 'button:has-text("Сообщение")']:
                btn = page.locator(btn_sel)
                if btn.count() > 0:
                    btn.click()
                    time.sleep(2)
                    for ta_sel in ['textarea[placeholder*="Message"]', 'textarea[placeholder*="Сообщение"]']:
                        textarea = page.locator(ta_sel)
                        if textarea.count() > 0:
                            textarea.fill(message[:300])
                            time.sleep(1)
                            for send_sel in ['button:has-text("Send")', 'button:has-text("Отправить")']:
                                send = page.locator(send_sel)
                                if send.count() > 0:
                                    send.click()
                                    time.sleep(2)
                                    page.close()
                                    return True
            page.close()
            return False
        except Exception as e:
            print(f"  ошибка tiktok: {e}")
            return False

    def send_discord(self, webhook_url, message):
        if not webhook_url:
            return False
        try:
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
            for ta_sel in ['textarea[placeholder*="Сообщение"]', 'textarea[placeholder*="Message"]']:
                textarea = page.locator(ta_sel)
                if textarea.count() > 0:
                    textarea.fill(message[:2000])
                    time.sleep(1)
                    for send_sel in ['button:has-text("Отправить")', 'button:has-text("Send")']:
                        send = page.locator(send_sel)
                        if send.count() > 0:
                            send.click()
                            time.sleep(2)
                            page.close()
                            return True
            page.close()
            return False
        except Exception as e:
            print(f"  ошибка discord: {e}")
            return False

    def send_telegram(self, profile_url, message):
        if not profile_url:
            return False
        try:
            username = profile_url.rstrip("/").split("/")[-1]
            if not username:
                return False
            print(f"  telegram @{username}")
            print("  [!] telegram: используйте Bot API")
            return False
        except Exception as e:
            print(f"  ошибка telegram: {e}")
            return False

def main():
    print(f"стримеров: {len(contacts)}")
    print(f"шаблонов: {len(letter_templates)}")

    sender = SocialSender()
    sender.start()

    sent = 0
    success = 0

    try:
        for username, links in contacts.items():
            if not links:
                continue
            template = random.choice(letter_templates) if letter_templates else {"subject": "", "body": ""}
            body = template.get("body", "").replace("{streamer_name}", username).replace("{manager_name}", "Алексей").replace("{casino_name}", "Lucky Star")
            msg = f"{template.get('subject', '')}\n\n{body}" if template.get("subject") else body

            available = [s for s, l in links.items() if l]
            if not available:
                continue

            print(f"\n{username}: {', '.join(available)}")

            ok = False
            for social, url in links.items():
                if not url:
                    continue
                if social == "instagram":
                    if sender.send_instagram(url, msg):
                        success += 1
                        ok = True
                        time.sleep(3)
                elif social == "twitter":
                    if sender.send_twitter(url, msg):
                        success += 1
                        ok = True
                        time.sleep(3)
                elif social == "tiktok":
                    if sender.send_tiktok(url, msg):
                        success += 1
                        ok = True
                        time.sleep(3)
                elif social == "discord":
                    if sender.send_discord(url, msg):
                        success += 1
                        ok = True
                        time.sleep(3)
                elif social == "telegram":
                    if sender.send_telegram(url, msg):
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