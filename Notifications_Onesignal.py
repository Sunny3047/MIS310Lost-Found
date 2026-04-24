# notifications.py - Send push notifications via OneSignal

import requests
from onesignal_config import ONESIGNAL_APP_ID, ONESIGNAL_API_KEY, ONESIGNAL_API_URL


def send_lost_found_notification(report_type, item_name, location):
    """
    Sends a notification when a new lost/found item is reported.
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Key {ONESIGNAL_API_KEY}"
    }

    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "included_segments": ["All Subscribers"],
        "headings": {
            "en": "📢 New Lost & Found Report"
        },
        "contents": {
            "en": f"{report_type}: {item_name} reported at {location}"
        }
    }

    try:
        response = requests.post(
            ONESIGNAL_API_URL,
            json=payload,
            headers=headers,
            timeout=10
        )

        print("Status:", response.status_code)
        print("Response:", response.text)

    except Exception as e:
        print("Error sending notification:", e)