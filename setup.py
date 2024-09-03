import os

def check_env_vars(timestamp):
    filename = ".env"
    if not os.path.exists(filename):
        print(f"[{timestamp}] Open .env to set up your Twitch API credentials!")
        empty_env = ["client_id = """,
                    "client_secret = """]

        with open(".env", "w") as env:
            env.write("\n".join(empty_env))

        exit()

    if not os.getenv("client_id") or not os.getenv("client_secret"):
        print(f"[{timestamp}] client_id or client_secret empty. Open .env to set up your Twitch API credentials!")
        exit()


def check_streamers_list(streamers_file, timestamp):
    if not os.path.exists(streamers_file):
        print(f"[{timestamp}] Open {streamers_file} to add your favorite streamers!")
        default_streamers = ["# Add streamer names on separate lines, like this:",
                         "MattEU",
                         "lirik",
                         "shxtou"]
        
        with open(streamers_file, "w") as file:
            file.write("\n".join(default_streamers))

        exit()