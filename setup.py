import os
import json
import logging

def check_and_load_config():
    filename = "config.json"

    if not os.path.exists(filename):
        # Define the configuration dictionary with default values
        config_data = {
            "check_interval": 15,
            "max_idle_duration": 300
        }

        # Write the configuration dictionary to a JSON file
        with open(filename, 'w') as file:
            json.dump(config_data, file, indent=4)

        logging.info(f"{filename} created successfully with default values.")
    
    with open(filename, 'r') as file:
        config = json.load(file)
    return config

def check_env_vars():
    filename = ".env"
    if not os.path.exists(filename):
        logging.warn(f"Open .env to set up your Twitch API credentials!")
        empty_env = ["client_id = """,
                    "client_secret = """]

        with open(".env", "w") as env:
            env.write("\n".join(empty_env))

        exit()

    if not os.getenv("client_id") or not os.getenv("client_secret"):
        logging.warn(f"client_id or client_secret empty. Open .env to set up your Twitch API credentials!")
        exit()


def check_streamers_list(streamers_file):
    if not os.path.exists(streamers_file):
        logging.info(f"Open {streamers_file} to add your favorite streamers!")
        default_streamers = ["# Add streamer names on separate lines, like this:",
                         "MattEU",
                         "lirik",
                         "shxtou"]
        
        with open(streamers_file, "w") as file:
            file.write("\n".join(default_streamers))

        exit()