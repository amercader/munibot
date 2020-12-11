import argparse
import sys
from urllib.parse import parse_qs, urlparse

from .config import load_config, load_profiles, get_logger
from .image import create_image
from .tweet import get_verify_auth, send_tweet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=["tweet", "create", "tokens"],
        help="""Action to perform. \"tweet\" sends out a tweet, \"create\" just generates the image locally. Use \"tokens\" to get the API access tokens for a bot""",
    )

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
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="""
    Output path for the generated image (Only used with "create"). Defaults to a <id>.jpg file in the current folder.
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
        if args.output:
            output = args.output
        else:
            output = f"{id_}.jpg"
        log.info(f'Starts: create image for feature {id_} on profile {args.profile}')
        create_image(profile, id_, output)
    elif args.command == "tweet":

        log.info(f'Start: sending tweet for feature {id_} on profile {args.profile}')
        text = profile.get_text(id_)
        img = create_image(profile, id_)
        lon, lat = profile.get_lon_lat(id_)

        send_tweet(profile, id_, text, img, lon, lat)
    elif args.command == "tokens":
        auth = get_verify_auth()
        verify_url = auth.get_authorization_url()

        oauth_token = parse_qs(urlparse(verify_url).query)["oauth_token"][0]

        msg = f"""
Please visit the following URL logged in as the Twitter bot account for this profile, authorize the application and input the verification code shown.

        {verify_url}

Verification code: """.strip()

        verification_code = input(msg)

        auth.request_token = {
            "oauth_token": oauth_token,
            "oauth_token_secret": verification_code,
        }

        access_token, access_token_secret = auth.get_access_token(verification_code)

        print(
            f"""
Done, access tokens for profile {args.profile}:

twitter_access_token={access_token}
twitter_access_token_secret={access_token_secret}
"""
        )
