import sys
import argparse

from .config import load_config, load_profiles
from .image import create_image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "profile",
        help="""Profile to use to generate the image / tweet. Must be one of the ones available""",
    )
    parser.add_argument(
        "--id",
        "-i",
        help="""
        Identifier of the administrative unit to create an image of.
        If not provided the relevant profile will provide one
        (generally a random one)""",
    )
    parser.add_argument(
        "--config",
        "-c",
        default="munibot.ini",
        help="""
    Path to the configuration ini file. Defaults to a "munibot.ini" in the same
    folder the command is run on.
    """,
    )

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
