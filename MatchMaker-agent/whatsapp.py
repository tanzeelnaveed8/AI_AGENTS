import chainlit as cl
import os
from agents import function_tool
import requests

@function_tool
def send_whatsapp_message(number: str, message: str) -> str:
    """
    uses the ultraMSG api to send a custom whatsapp message to the specificd
    phone number. return sucess message if sent sucessfully, or error message if the request fails.
    """
    instance_id = os.getenv("INSTANCE_ID")
    ultra_token = os.getenv("ULTRA_TOKEN")

    url = f"https://api.ultramsg.com/{instance_id}/messages/chat"

    payload = {
        "token": ultra_token,
        "to": number,
        "body": message
    }

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        return "Message sent successfully!"
    else:
        return f"Failed to send message: {response.text}"
