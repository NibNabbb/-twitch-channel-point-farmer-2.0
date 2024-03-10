import os
import requests
import time
from datetime import datetime
import logging
import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class TwitchAuth:
    API_BASE_URL = "https://api.twitch.tv/helix"
    OAUTH_URL = "https://id.twitch.tv/oauth2/token"

    def __init__(self, client_id, client_secret, grant_type="client_credentials"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = grant_type
        self.access_token = None
        self.expires_in = None
        self.token_type = None

    def authenticate(self):
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": self.grant_type
        }

        try:
            response = requests.post(self.OAUTH_URL, data=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error during authentication: {str(e)}")
            return

        response_json = response.json()
        self.access_token = response_json["access_token"]
        self.expires_in = response_json["expires_in"]
        self.token_type = response_json["token_type"]

    def get_live_streams(self, user_id=None, user_login=None, game_id=None, stream_type="all", language=None, limit=20, before=None, after=None):
        url = f"{self.API_BASE_URL}/streams"

        params = {
            "user_id": user_id,
            "user_login": user_login,
            "game_id": game_id,
            "type": stream_type,
            "language": language,
            "first": limit,
            "before": before,
            "after": after
        }

        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting live streams: {str(e)}")
            return None

        return response.json()

    def get_users_info(self, user_id=None, user_login=None):
        url = f"{self.API_BASE_URL}/users"

        params = {
            "id": user_id,
            "login": user_login
        }

        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting user info: {str(e)}")
            return None

        return response.json()

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def setup_logging():
    logs_folder = "logs"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    # Remove older log files, keeping only the three most recent ones
    existing_logs = sorted(glob.glob(os.path.join(logs_folder, "log-*.log")), key=os.path.getctime, reverse=True)
    logs_to_keep = existing_logs[:2]

    for log_file in existing_logs:
        if log_file not in logs_to_keep:
            os.remove(log_file)

    log_filename = f"log-{get_timestamp()}.log"

    logging.basicConfig(
        filename=os.path.join(logs_folder, log_filename),
        level=logging.INFO,
        format="[%(asctime)s] (%(levelname)s): %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def read_streamers_from_file(filename="streamers.txt"):
    streamers = []

    if os.path.exists(filename):
        with open(filename, "r") as file:
            for line in file:
                # Ignore comments and empty lines
                if line.strip() and not line.startswith("#"):
                    streamers.append(line.strip())

    return streamers

def write_default_streamers(filename="streamers.txt"):
    default_streamers = ["# Add streamer names on separate lines, like this:",
                         "MattEU",
                         "lirik",
                         "shxtou"]

    with open(filename, "w") as file:
        file.write("\n".join(default_streamers))

def download_profile_image(user_info, pfp_folder="pfp"):
    if not os.path.exists(pfp_folder):
        os.makedirs(pfp_folder)

    streamer_name = user_info['login']
    profile_image_path = os.path.join(pfp_folder, f"profile_image_{streamer_name}.png")

    if not os.path.exists(profile_image_path):
        profile_image_url = user_info['profile_image_url']
        response = requests.get(profile_image_url)

        if response.status_code == 200:
            with open(profile_image_path, 'wb') as img_file:
                img_file.write(response.content)
                logging.info(f"Downloaded profile image for {streamer_name}")
        else:
            logging.error(f"Failed to download profile image for {streamer_name}. Status code: {response.status_code}")

def init_browser():
    options = webdriver.ChromeOptions()
    options.add_argument(rf"--user-data-dir=C:\Users\{os.getenv('USERNAME')}\AppData\Local\Google\Chrome\User Data")
    options.add_argument(r'--profile-directory=Profile 1')
    options.add_experimental_option("detach", True)
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
    return webdriver.Chrome(options=options)

first_time_run = True
def browser_open(streamer_login):
    global driver
    global first_time_run

    if not first_time_run:
        driver.switch_to.new_window('tab')
    driver.get(f"https://www.twitch.tv/{streamer_login}")
    first_time_run = False
    return driver.current_window_handle

def check_browser_open():
    global driver

    try:
        # Check if the driver is still open and has at least one window handle
        return driver and driver.window_handles
    except Exception:
        return False

def check_live_status(check_interval=15):
    global driver
    global first_time_run

    # Check if the interval is too small, avoid spamming Twitch servers.
    if check_interval < 15:
        print(f"[{get_timestamp()}] Interval has to be equal to or more than 15!")
        exit()

    next_check_time = time.time()
    live_streamers = []  # List of dictionaries containing streamer info
    recently_offline_streamers = []

    while True:
        current_time = time.time()

        if current_time >= next_check_time:
            # Read streamer names from "streamers.txt"
            streamers = read_streamers_from_file(streamers_file)

            for streamer_login in streamers:
                streams_data = auth.get_live_streams(user_login=streamer_login)

                if streams_data and streams_data.get("data"):
                    timestamp = get_timestamp()

                    # Get user info to download profile image
                    user_info = auth.get_users_info(user_login=streamer_login)
                    if user_info and user_info.get("data"):
                        download_profile_image(user_info['data'][0])

                    streamer_info = next((info for info in live_streamers if info['streamer_login'] == streamer_login), None)

                    if not streamer_info:
                        if not check_browser_open():
                            first_time_run = True
                            driver = init_browser()
                            logging.info("Browser initiated!")

                        message = f"{streamer_login} is live!"
                        print(f"[{timestamp}] {message}")
                        logging.info(message)

                        current_window_handle = browser_open(streamer_login)

                        live_streamers.append({'streamer_login': streamer_login, 'window_handle': current_window_handle})
                    else:
                        stream_window = next((info['window_handle'] for info in live_streamers if info['streamer_login'] == streamer_login), None)
                        driver.switch_to.window(stream_window)

                else:
                    timestamp = get_timestamp()
                    streamer_info = next((info for info in live_streamers if info['streamer_login'] == streamer_login), None)

                    if streamer_info:
                        if streamer_info in recently_offline_streamers:
                            message = f"{streamer_login} is not live."
                            print(f"[{timestamp}] {message}")
                            logging.info(message)

                            live_streamers.remove(streamer_info)

                            stream_window = streamer_info['window_handle']

                            try:
                                driver.switch_to.window(stream_window)
                                driver.close()
                                recently_offline_streamers.remove(streamer_info)
                            except Exception:
                                print(f"[{timestamp}] Could not close the tab for {streamer_login}!")
                                logging.error(f"Could not close the tab for {streamer_login}!")
                        else:
                            print(f"[{timestamp}] Stream not found for {streamer_login}, retrying in {check_interval} seconds!")

                            recently_offline_streamers.append(streamer_info)

            # Update the next check time
            next_check_time = current_time + check_interval

        # This allows the loop to avoid consuming too much CPU
        time.sleep(1)

if __name__ == "__main__":
    # Setup logging
    setup_logging()

    # Twitch app credentials
    client_id = "hsgyiosq65o77sx5h34uxfmmwts0an"
    client_secret = "ysikujvxm4pzp1je10nccpaw4ylerx"

    # Create an instance of TwitchAuth
    auth = TwitchAuth(client_id, client_secret)

    # Authenticate to obtain the access token
    auth.authenticate()

    # Check if "streamers.txt" exists
    streamers_file = "streamers.txt"

    if not os.path.exists(streamers_file):
        print(f"[{get_timestamp()}] Open {streamers_file} to add your favorite streamers!")
        write_default_streamers(streamers_file)
        exit()

    # Start the loop to check if the streamer is live
    check_live_status()
