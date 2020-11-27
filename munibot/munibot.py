import os
import sys
import argparse
import configparser

from .config import load_config, load_profiles
from .image import create_image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("profile")
    parser.add_argument("id")
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

    create_image(args.profile, args.id)
