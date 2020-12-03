import tempfile

import tweepy

from .config import config


def get_auth(profile):

    profile_config = config["profile:" + profile.id]

    auth = tweepy.OAuthHandler(
        config["twitter"]["api_key"],
        config["twitter"]["api_key_secret"],
    )
    auth.set_access_token(
        profile_config["twitter_access_token"],
        profile_config["twitter_access_token_secret"],
    )

    return auth


def send_tweet(profile, id_, text, image):

    api = tweepy.API(get_auth(profile))

    with tempfile.NamedTemporaryFile(suffix=".jpg") as f:
        f.write(image.getbuffer())
        media = api.media_upload(f.name, file=f)

    status = api.update_status(text, media_ids=[media.media_id])

    profile.after_tweet(id_, status.id)
