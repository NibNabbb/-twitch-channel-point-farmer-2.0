import os
import sys
import time
import logging
import msvcrt
from dotenv import load_dotenv

from browser import init_browser, check_browser_open  # Import browser functions
from logging_handler import setup_logging  # Import logging function
from twitchauth import TwitchAuth  # Import TwitchAuth class
from setup import first_time_setup, check_and_load_config, check_streamers_list, check_env_vars # Import setup functions
from pfp import download_profile_image  # Import pfp download function
from idle import check_idle_duration # Import idle detection functions
from notification import send_notification # Import notification function
from streamers import read_streamers_from_file # Import list reading functions
from argparser import parseargs # Import arg check function

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
    minimum_check_interval = len(read_streamers_from_file(config.get('active_list'))) * 5
    if check_interval < 15:
        logging.error("Interval has to be equal to or more than 15!")
        print("Press any key to continue...")
        msvcrt.getch()
        sys.exit()
    elif check_interval < minimum_check_interval:
        logging.error(f"Interval has to be equal to or more than {minimum_check_interval}!")
        print("Press any key to continue...")
        msvcrt.getch()
        sys.exit()

    next_check_time = time.time()
    live_streamers = []  # List of dictionaries containing streamer info
    recently_offline_streamers = []
    external_closed_warning = False

    while True:
        current_time = time.time()

        # Check user inactivity
        idle_duration = check_idle_duration()

        if current_time >= next_check_time:
            # Read streamer names from the streamer list
            streamers = read_streamers_from_file(config.get('active_list'))

            # Loop through all streamers read from the streamer list
            for streamer_login in streamers:
                # Checks if a streamer is live, and gets relevant stream data
                streams_data = auth.get_live_streams(user_login=streamer_login)

                # If a streamer is live
                if streams_data and streams_data.get("data"):
                    # Get user info to download profile image
                    user_info = auth.get_users_info(user_login=streamer_login)
                    if config.get('notification') and user_info and user_info.get("data"):
                        download_profile_image(user_info['data'][0])

                    # Some black magic to find out if the streamer is already known to be live
                    streamer_info = next((info for info in live_streamers if info['streamer_login'] == streamer_login), None)

                    # If the streamer is known to be live, remove from recently offline streamers
                    if streamer_info in recently_offline_streamers:
                        recently_offline_streamers.remove(streamer_info)

                    # If not already known to be live or not already open in managed browser window
                    if not streamer_info or not streamer_info['open_in_browser']:
                        # Get the stream title
                        for stream in streams_data["data"]:
                            stream_title = stream['title']
                        
                        # If not already known to be live, log that the streamer is now live
                        if not streamer_info in live_streamers:
                            logging.info(f"{streamer_login} is live!")

                        # If the computer is considered "idle", and the streamer isn't already known to be live, and a browser tab has not already been opened
                        if idle_duration > config.get('max_idle_duration'):
                            if config.get('autofarming'):
                                # Removing streamer from live streamers to re-add updated info later
                                if streamer_info in live_streamers:
                                    live_streamers.remove(streamer_info)

                                # Open a managed browser window with tabs for each live streamer
                                if not check_browser_open(driver):
                                    first_time_run = True
                                    driver = init_browser()
                                current_window_handle = stream_open(streamer_login)
                                live_streamers.append({'streamer_login': streamer_login, 'window_handle': current_window_handle, 'open_in_browser': True})
                        
                        # If the computer is not considered "idle", and the streamer isn't already known to be live, or a notification has not been sent already
                        elif not streamer_info or not streamer_info['notification_sent']:
                            # If notifications are enabled, send notification
                            if config.get('notification'):
                                # Removing streamer from live streamers to re-add updated info later
                                if streamer_info in live_streamers:
                                    live_streamers.remove(streamer_info)

                                # Send a non-intrusive notification to user
                                send_notification(user_info['data'][0], stream_title)

                            live_streamers.append({'streamer_login': streamer_login, 'open_in_browser': False, 'notification_sent': True})

                    # If already known to be live or already open in managed browser window
                    else:
                        stream_window = next((info['window_handle'] for info in live_streamers if info['streamer_login'] == streamer_login), None)

                        # Switch to streamer tab in managed browser
                        if check_browser_open(driver):
                            driver.switch_to.window(stream_window)
                        else:
                            if not external_closed_warning:
                                logging.warning("Browser has been closed externally!")
                                external_closed_warning = True

                # If a streamer is not live
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

    # Get relevant launch arguments
    skip_intro = parseargs()

    # Setup logging
    logging = setup_logging()

    # Load first time setup
    first_time_setup(skip_intro)

    # Check base config        
    config = check_and_load_config()

    # Check environment variables
    check_env_vars()

    # Create an instance of TwitchAuth
    auth = TwitchAuth(os.getenv("client_id"), os.getenv("client_secret"))

    # Authenticate to obtain the access token
    auth.authenticate()

    # Check if streamers list exists
    streamers_file = config.get('active_list')
    check_streamers_list(streamers_file)

    # Define global variables
    driver = None
    first_time_run = True

    # Script is ready
    logging.info("Script is ready!")

    # Start the loop to check if the streamer is live
    check_stream_status()
