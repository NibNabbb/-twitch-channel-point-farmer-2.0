import os
import logging
from winotify import Notification

def send_notification(user_info, stream_title):
    streamer_login = user_info['login']
    streamer_name = user_info['display_name']

    image_path = os.path.abspath(f"pfp/profile_image_{streamer_login}.png")
    
    toast = Notification(app_id="Twitch Channel Point Farmer",
                    title=f"{streamer_name} is live! Go farm some points!",
                    msg=f"{stream_title}",
                    duration="short",
                    icon=image_path)
    toast.show()

    logging.info("Notification sent!")