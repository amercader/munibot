import sys
import argparse

from .config import load_config, load_profiles
from .image import create_image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("profile")
    parser.add_argument("--id", "-i")
    parser.add_argument("--config", "-c", default="munibot.ini")

    args = parser.parse_args()
    try:
        load_config(args.config)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    profiles = load_profiles()
    if args.profile not in profiles:
        print(f"Unknown profile: {args.profile}")
        sys.exit(1)

    if args.id:
        id_ = args.id
    else:
        profile = profiles[args.profile]()
        id_ = profile.get_next_id()

    if id_ is None:
        print("No more images to create!")
        sys.exit()

    create_image(args.profile, id_)
