import os
import requests
import logging
from datetime import datetime, timedelta

def download_profile_image(user_info, pfp_folder="pfp"):
    if not os.path.exists(pfp_folder):
        os.makedirs(pfp_folder)

    streamer_name = user_info['login']
    profile_image_path = os.path.join(pfp_folder, f"profile_image_{streamer_name}.png")
    
    file_exists = os.path.exists(profile_image_path)

    # Check if the file exists and if it is older than 30 days
    if file_exists:
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(profile_image_path))
        current_time = datetime.now()
        file_age = current_time - file_mod_time

        if file_age > timedelta(days=30):
            # File is older than 30 days, delete it
            os.remove(profile_image_path)
            logging.info(f"Deleted old profile image for {streamer_name}")

            file_exists = False  # Indicate that the file needs to be downloaded

    if not file_exists:
        profile_image_url = user_info['profile_image_url']
        response = requests.get(profile_image_url)

        if response.status_code == 200:
            with open(profile_image_path, 'wb') as img_file:
                img_file.write(response.content)
                logging.info(f"Downloaded profile image for {streamer_name}")
        else:
            logging.error(f"Failed to download profile image for {streamer_name}. Status code: {response.status_code}")

