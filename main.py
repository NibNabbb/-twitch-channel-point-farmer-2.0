import os
import time
import logging
from dotenv import load_dotenv

from browser import init_browser, check_browser_open  # Import browser functions
from logging_handler import setup_logging  # Import logging function
from twitchauth import TwitchAuth  # Import TwitchAuth class
from setup import check_and_load_config, check_streamers_list, check_env_vars # Import setup functions
from pfp import download_profile_image  # Import pfp download function
from idle import check_idle_duration # Import idle detection functions
from notification import send_notification # Import notification function

def read_streamers_from_file():
    filename=config.get('list')
    streamers = []

    if os.path.exists(filename):
        with open(filename, "r") as file:
            for line in file:
                # Ignore comments and empty lines
                if line.strip() and not line.startswith("#"):
                    streamers.append(line.strip())

    return streamers

def stream_open(streamer_login):
    global driver
    global first_time_run

    if not first_time_run:
        driver.switch_to.new_window('tab')
    driver.get(f"https://www.twitch.tv/{streamer_login}")
    first_time_run = False
    return driver.current_window_handle

def check_stream_status():
    global driver
    global first_time_run

    check_interval = config.get('check_interval')

    # Check if the interval is too small, avoid spamming Twitch servers as well as giving browser tabs time to load.
    minimum_check_interval = len(read_streamers_from_file()) * 5
    if check_interval < 15:
        logging.error("Interval has to be equal to or more than 15!")
        exit()
    elif check_interval < minimum_check_interval:
        logging.error(f"Interval has to be equal to or more than {minimum_check_interval}!")
        exit()

    next_check_time = time.time()
    live_streamers = []  # List of dictionaries containing streamer info
    recently_offline_streamers = []

    while True:
        current_time = time.time()

        # Check user inactivity
        idle_duration = check_idle_duration()

        if current_time >= next_check_time:
            # Read streamer names from "streamers.txt"
            streamers = read_streamers_from_file()

            for streamer_login in streamers:
                streams_data = auth.get_live_streams(user_login=streamer_login)

                if streams_data and streams_data.get("data"):
                    # Get user info to download profile image
                    user_info = auth.get_users_info(user_login=streamer_login)
                    if user_info and user_info.get("data"):
                        download_profile_image(user_info['data'][0])

                    streamer_info = next((info for info in live_streamers if info['streamer_login'] == streamer_login), None)

                    if streamer_info in recently_offline_streamers:
                        recently_offline_streamers.remove(streamer_info)

                    if not streamer_info or not streamer_info['open_in_browser']:
                        for stream in streams_data["data"]:
                            stream_title = stream['title']
                        
                        if not streamer_info in live_streamers:
                            logging.info(f"{streamer_login} is live!")

                        if idle_duration > config.get('max_idle_duration'):
                            if streamer_info in live_streamers:
                                live_streamers.remove(streamer_info)

                            if config.get('autofarming'):
                                if not check_browser_open(driver):
                                    first_time_run = True
                                    driver = init_browser()
                                current_window_handle = stream_open(streamer_login)
                                live_streamers.append({'streamer_login': streamer_login, 'window_handle': current_window_handle, 'open_in_browser': True})
                        
                        elif not streamer_info or not streamer_info['notification_sent']:
                            if streamer_info in live_streamers:
                                live_streamers.remove(streamer_info)

                            if config.get('notification'):
                                # Send a non-intrusive notification to user
                                send_notification(user_info['data'][0], stream_title)

                            live_streamers.append({'streamer_login': streamer_login, 'open_in_browser': False, 'notification_sent': True})

                    else:
                        stream_window = next((info['window_handle'] for info in live_streamers if info['streamer_login'] == streamer_login), None)
                        driver.switch_to.window(stream_window)

                else:
                    streamer_info = next((info for info in live_streamers if info['streamer_login'] == streamer_login), None)

                    if streamer_info:
                        if streamer_info in recently_offline_streamers:
                            logging.info(f"{streamer_login} is not live.")

                            live_streamers.remove(streamer_info)

                            stream_window = streamer_info['window_handle']

                            if stream_window:
                                try:
                                    driver.switch_to.window(stream_window)
                                    driver.close()
                                    recently_offline_streamers.remove(streamer_info)
                                except Exception:
                                    logging.error(f"Could not close the tab for {streamer_login}!")
                        else:
                            logging.info(f"Stream not found for {streamer_login}, retrying in {check_interval} seconds!")

                            recently_offline_streamers.append(streamer_info)

            # Update the next check time
            next_check_time = current_time + check_interval

        # This allows the loop to avoid consuming too much CPU
        time.sleep(1)

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    # Setup logging
    logging = setup_logging()

    # Check base config
    config = check_and_load_config()

    # Check environment variables
    check_env_vars()

    # Create an instance of TwitchAuth
    auth = TwitchAuth(os.getenv("client_id"), os.getenv("client_secret"))

    # Authenticate to obtain the access token
    auth.authenticate()

    # Check if streamers list exists
    streamers_file = config.get('list')
    check_streamers_list(streamers_file)

    # Define global variables
    driver = None
    first_time_run = True

    # Start the loop to check if the streamer is live
    check_stream_status()
