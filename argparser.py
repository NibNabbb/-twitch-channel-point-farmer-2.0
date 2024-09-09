import argparse

def chackargs():
    # Create the parser
    parser = argparse.ArgumentParser("Twitch Channel Point Farmer 2.0")

    # Add --skip-intro / -skipintro flag
    parser.add_argument(
        "--skip-intro", 
        "-skipintro", 
        action="store_true",  # This makes the argument a flag, storing True if present
        help="Skips introduction explanation and only asks questions relevant to first time setup"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Access the flag (will be True if --skip-intro or -skipintro is provided)
    return args.skip_intro