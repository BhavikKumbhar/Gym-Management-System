import webbrowser
import urllib.parse

def send_whatsapp_reminder(phone, name, expiry_date):
    message = f"""
Hello {name},

Your gym membership will expire on {expiry_date}.
Please renew your plan to avoid interruption.

– Gym Management
"""
    encoded_message = urllib.parse.quote(message)
    url = f"https://wa.me/{phone}?text={encoded_message}"
    webbrowser.open(url)
