import argparse
import json
import os
import sys
from urllib.parse import parse_qs, urlparse

from .config import config, load_config, load_profiles, get_logger
from .image import create_image
from .mastodon import send_status

DUMP_FILE_TEMPLATE = """
window.MunibotPosts = {}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=["post", "create", "profiles", "dump"],
        help="""
Action to perform. "post" sends out a post, "create" just generates the image locally.
"profiles" lists all installed profiles and "dump" return a JS file that can be used in
the map app.""",
    )
    parser.add_argument(
        "profile",
        nargs="?",
        help="""Profile to use to generate the image / post. Must be one of the ones available""",
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
    parser.add_argument(
        "--output-dir",
        "-o",
        default=None,
        help="""
    Output directory for the generated image (Only used with "create" and "post"). Defaults to the the current folder in "create" and None in "post" (don't save it) .
    """,
    )

    args = parser.parse_args()

    if args.command != "profiles" and not args.profile:
        print("munibot: error: the following arguments are required: profile")
        sys.exit(1)

    try:
        load_config(args.config)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    profiles = load_profiles()

    if args.command == "profiles":

        if not profiles:
            print("No profiles found :(")
            sys.exit()
        num = len(profiles.keys())
        print(f"{num} profile found:" if num == 1 else f"{num} profiles found:")
        for name, profile in profiles.items():
            print(f"{name} - {profile.desc}")

        sys.exit()

    if args.profile not in profiles:
        print(f"Unknown profile: {args.profile}")
        sys.exit(1)

    profile = profiles[args.profile]()

    if args.id:
        id_ = args.id
    else:
        id_ = profile.get_next_id()

    if id_ is None:
        print("No more images to create!")
        sys.exit()

    log = get_logger(__name__)

    if args.command == "create":
        output = f"{id_}.jpg"
        if args.output_dir:
            output = os.path.join(args.output_dir, output)
        log.info(f"Start: create image for feature {id_} on profile {args.profile}")
        create_image(profile, id_, output)
    elif args.command == "post":
        if args.output_dir:
            output = os.path.join(args.output_dir, f"{id_}.jpg")
        else:
            output = None

        log.info(f"Start: sending status for feature {id_} on profile {args.profile}")
        text = profile.get_text(id_)
        img = create_image(profile, id_, output)

        send_status(profile, id_, text, img)
    elif args.command == "dump":

        if not hasattr(profile, "posts_dump"):
            print("Profile has no dump method")
            sys.exit(1)

        count, posts = profile.posts_dump()

        profile_config = config[f"profile:{profile.id}"]

        out = {
            "mastodon": {
                "host": profile_config["mastodon_api_base_url"],
                "account": profile_config["mastodon_account_name"],
                "posts": posts,
                "total": count,
                "posted": len(posts.keys())}
        }
        print(DUMP_FILE_TEMPLATE.format(json.dumps(out)))
