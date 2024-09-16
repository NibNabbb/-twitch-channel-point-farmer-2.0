# https://youtu.be/N3zf9q8mbWs?si=LyPk33lLR7qvRGPA

import os
import sys
import json
import logging
import time
from msvcrt import getch
from dotenv import load_dotenv

from streamers import read_streamers_from_file # Import list reading functions

def yes_or_no(value, default):
    if default:
        text = "yes"
    elif not default:
        text = "no"

    if value == "y" or value == "yes":
        value = True
    elif value == "n" or value == "no":
        value = False
    else:
        print(f"Invalid syntax. Defaulting to {text}.")
        print()
        value = default
    return value

def first_time_setup(skip_intro):
    # Load environment variables from .env file
    load_dotenv()

    if os.path.exists("config.json"):
        with open("config.json", 'r') as file:
            config = json.load(file)
        streamers_file = config.get('active_list')
    else:
        streamers_file = "streamers.txt"

    # Step 1: Introduction
    if not os.path.exists(".env"):
        if not os.path.exists("fts.json"):
            # Write the configuration dictionary to a JSON file
            with open("fts.json", 'w') as file:
                json.dump({}, file, indent=4)
        with open("fts.json", 'r') as file:
            fts_data = json.load(file)


        if not fts_data.get('skip_intro') and not skip_intro:
            print("Have you used this script before? (y/n)")
            skip_intro = input()
            print()

            skip_intro = yes_or_no(skip_intro, False)
        
        skip_intro = {"skip_intro": skip_intro}
        fts_data.update(skip_intro)
        # Write the configuration dictionary to a JSON file
        with open("fts.json", 'w') as file:
            json.dump(fts_data, file, indent=4)
        
        if not fts_data.get('skip_intro') and not skip_intro.get("skip_intro"):
            print("Hi! Welcome to the Twitch Channel Point Farmer 2.0!")
            time.sleep(2)
            print("Let's set up the basics.")
            time.sleep(2)
            print("First you will have to get the Twitch API credentials and place them in the .env file that will be created shortly. Once that is done you can restart the script to proceed with the setup!")
            time.sleep(2)
            print()
        else:
            print(".env file created! Please enter your Twitch API credentials.")
            print()

        check_env_vars(True)
    # Step 1: Fail condition
    if os.getenv("client_id") == "" or os.getenv("client_secret") == "":
        print("Seems like you forgot to enther the Twitch API credentials into the .env file. Once you've done that, you can proceed with the setup.")
        print("Press any key to continue...")
        getch()
        sys.exit()

    # Step 2: Streamer list
    if not os.path.exists(streamers_file):
        if not os.path.exists("fts.json"):
            # Write the configuration dictionary to a JSON file
            with open("fts.json", 'w') as file:
                json.dump({}, file, indent=4)
        with open("fts.json", 'r') as file:
            fts_data = json.load(file)

        if not fts_data.get('skip_intro') and not skip_intro:
            print("Now that the Twithc API credentials are in place, let's create the streamer list.")
            time.sleep(2)
            print("You can add as many streamers to this list as you want, but keep in mind that the more streamers you add, the slower the program will get.")
            time.sleep(2)
            print("First, we need to name the list. By default, the name is 'streamers.txt', but you can name it whatever you want!")
            time.sleep(2)
            print()
        
        if os.path.exists("config.json"):
            if config.get("active_list"):
                default_streamer_list = config.get("active_list")
        else:
            default_streamer_list = "streamers.txt"
        
        print(f"What would you like to name the list? ({default_streamer_list})")
        streamers_file = input()
        print()

        if streamers_file == "":
            streamers_file = default_streamer_list

        streamers_file = {"streamers_file": streamers_file}
        fts_data.update(streamers_file)
        # Write the configuration dictionary to a JSON file
        with open("fts.json", 'w') as file:
            json.dump(fts_data, file, indent=4)

        if not fts_data.get('skip_intro') and not skip_intro: 
            print(f"Great! Now all you have to do is open {streamers_file.get('streamers_file')} to add your favorite streamers! Restart the the script when you're ready to proceed with the setup!")
            print()
        else:
            print(f"Open {streamers_file.get('streamers_file')} to add your favorite streamers!")
            print()

        check_streamers_list(streamers_file.get('streamers_file'), True)

    # Step 3: Config
    if not os.path.exists("config.json"):
        if not os.path.exists("fts.json"):
            # Write the configuration dictionary to a JSON file
            with open("fts.json", 'w') as file:
                json.dump({}, file, indent=4)
        with open("fts.json", 'r') as file:
            fts_data = json.load(file)


        if not fts_data.get('skip_intro') and not skip_intro:
            print("This is the last step. Now we just have to set up the basic config.")
            time.sleep(2)
            print("You can change these settings at any time in the 'config.json' file.")
            time.sleep(2)
            print()

        with open("fts.json", 'r') as file:
            fts_data = json.load(file)

        if fts_data.get('streamers_file'):
            streamers_file = fts_data.get('streamers_file')
        else:
            streamers_file = "streamers.txt"

        minimum_check_interval = len(read_streamers_from_file(streamers_file)) * 5
        if minimum_check_interval > 15:
            default_check_interval = minimum_check_interval
        else:
            default_check_interval = 15

        if not fts_data.get('skip_intro') and not skip_intro:
            print("First off, the check interval. This is the interval between each check in with Twitch to check if the streamers are live.")
            time.sleep(2)
            print("The absolute minimum for this interval is 15 seconds, but there is also a dynamic minimum. For every streamer added in the list, 5 seconds are added to the dynamic limit.")
            time.sleep(2)
            print(f"Based of the current list ({streamers_file}), the minimum is {default_check_interval}.")
            time.sleep(2)
            print("You can also choose to use a dynamic check interval, this means the check interval will always be the minimum allowed by the dynamic minimum and the absolute minimum.")
            time.sleep(2)
            print()
        print("Do you want to use a dynamic check interval? (y/n)")
        dynamic_check_interval = input()
        print()
        dynamic_check_interval = yes_or_no(dynamic_check_interval, True)

        if dynamic_check_interval:
            check_interval = default_check_interval
        else:
            print(f"What would you like the check interval to be? ({default_check_interval}).")
            check_interval = input()
            print()

            if check_interval == "":
                check_interval = default_check_interval
            else:
                int(check_interval)

        if not fts_data.get('skip_intro') and not skip_intro:
            print("Alright. Next up is the max idle duration. This is the ammount of time in seconds of inactivity before the computer is considered 'idle'.")
            time.sleep(2)
            print()
        print("Do you want to use the check interval time as the idle duration time as well? (y/n)")
        idle_duration_same_as_check_interval = input()
        print()
        idle_duration_same_as_check_interval = yes_or_no(idle_duration_same_as_check_interval, True)

        if idle_duration_same_as_check_interval:
            max_idle_duration = check_interval
        else:
            print("What would you like the max idle duration to be? (300)")
            max_idle_duration = input()
            print()

        if max_idle_duration == "":
            max_idle_duration = 300
        else:
            max_idle_duration = int(max_idle_duration)

        if not fts_data.get('skip_intro') and not skip_intro:
            print("Ok. Next up, do you want to enable notifications when the streamers go live? (y/n)")
        else:
            print("Do you want to enable notifications when the streamers go live? (y/n)")

        notification = input()
        print()
        notification = yes_or_no(notification, True)
        
        if not fts_data.get('skip_intro') and not skip_intro:
            print ("Ok. Next up, autofarming. This allows the script to open up chrome and 'watch' the streams when the streamers are live and the computer is 'idle'.")
            time.sleep(2)
            print("This allows the script to 'farm' channel points while you're away. (for legal reasons, this is a joke. please don't ban me twitch.)")
            time.sleep(2)
            print("Without this, the script will not be farming any channel points.")
            time.sleep(2)
            print()
        print("Do you wish to enable autofarming? (y/n)")

        autofarming = input()
        print()
        autofarming = yes_or_no(autofarming, True)
    
        config_data = {
            "check_interval": check_interval,
            "max_idle_duration": max_idle_duration,
            "notification": notification,
            "autofarming": autofarming,
            "active_list": streamers_file,
            "dynamic_check_interval": dynamic_check_interval,
            "idle_duration_same_as_check_interval": idle_duration_same_as_check_interval
        }

        # Write the configuration dictionary to a JSON file
        with open(("config.json"), 'w') as file:
            json.dump(config_data, file, indent=4)
        
        print("That's it! The script is now ready!")
        logging.info("First time setup complete!")
        time.sleep(2)

    if os.path.exists("fts.json"):
        os.remove("fts.json")

    # Load up the most recent config
    with open("config.json", 'r') as file:
        config = json.load(file)

    # Update dynamic check interval
    if config.get('dynamic_check_interval'):
        minimum_check_interval = len(read_streamers_from_file(streamers_file)) * 5
        if minimum_check_interval > 15:
            default_check_interval = minimum_check_interval
        else:
            default_check_interval = 15

        check_interval = {"check_interval": default_check_interval}
        config.update(check_interval)

        # Write the configuration dictionary to a JSON file
        with open("config.json", 'w') as file:
            json.dump(config, file, indent=4)

    # Update idle duration
    if config.get("idle_duration_same_as_check_interval"):
        max_idle_duration = config.get("check_interval")

        max_idle_duration = {"max_idle_duration": max_idle_duration}
        config.update(max_idle_duration)

        # Write the configuration dictionary to a JSON file
        with open("config.json", 'w') as file:
            json.dump(config, file, indent=4)
    


def check_and_load_config():
    filename = "config.json"

    if not os.path.exists(filename):
        logging.error("config.json could not be found!")
        print("Press any key to continue...")
        getch()
        sys.exit()
    
    with open(filename, 'r') as file:
        config = json.load(file)
    return config

def check_env_vars(fts = False):
    filename = ".env"
    if not os.path.exists(filename):
        if not fts: logging.warning(f"Open .env to set up your Twitch API credentials!")
        empty_env = ["client_id = """,
                    "client_secret = """]

        with open(".env", "w") as env:
            env.write("\n".join(empty_env))

        print("Press any key to continue...")
        getch()
        sys.exit()

    if not os.getenv("client_id") or not os.getenv("client_secret"):
        if not fts: logging.warning(f"client_id or client_secret empty. Open .env to set up your Twitch API credentials!")
        print("Press any key to continue...")
        getch()
        sys.exit()


def check_streamers_list(streamers_file, fts = False):
    if not os.path.exists(streamers_file):
        if not fts: logging.info(f"Open {streamers_file} to add your favorite streamers!")
        default_streamers = ["# Add streamer names on separate lines, like this:",
                         "MattEU",
                         "lirik",
                         "shxtou"]
        
        with open(streamers_file, "w") as file:
            file.write("\n".join(default_streamers))

        print("Press any key to continue...")
        getch()
        sys.exit()