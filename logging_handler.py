import os
import glob
from datetime import datetime
import logging

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def setup_logging():
    logs_folder = "logs"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    # Remove older log files, keeping only the two most recent ones
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

    return logging
