# utils.py

import requests

# Hardcoded values for now (use .env in production)
INSTANCE_ID = "instance133037"
TOKEN = "cgl2zdx2alz82t9p"

def send_whatsapp_message(to_number: str, message: str) -> bool:
    try:
        url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"

        payload = {
            "token": TOKEN,
            "to": to_number,
            "body": message
        }

        res = requests.post(url, data=payload)

        if res.status_code == 200:
            print("✅ WhatsApp message sent!")
            return True
        else:
            print(f"❌ Error: {res.status_code} - {res.text}")
            return False
    except Exception as e:
        print("❌ Exception while sending message:", e)
        return False
