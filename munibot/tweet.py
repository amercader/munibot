import tempfile

import tweepy

from .config import config, get_logger


def get_verify_auth():
    """
    Return a Tweepy authorization handler instance, with just the api key
    and secret set.

    This is generally used in the ``tokens`` command to request the bot account tokens.
    """
    auth = tweepy.OAuthHandler(
        config["twitter"]["api_key"],
        config["twitter"]["api_key_secret"],
        "oob",
    )

    return auth


def get_auth(profile):
    """
    Returns a Tweepy authorization handler instance using the access tokens for a
    particular profile.

    The returned handled can be used to interact with the Twitter API using the
    profile bot account.
    """

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


def send_tweet(profile, id_, text, image, lon=None, lat=None):
    """
    Publish a new tweet in the profile bot account.

    Uploads the provided image and posts a new status with the text provided.
    If provided, it also includes longitude and latitude information, but these
    are optional.

    After sending the tweet it calls the ``after_tweet()`` method of the provided
    profile, passing the feature id and the new tweet status id.

    :param profile: an instance of the profile class
    :type profile: object
    :param id_: the identifier of the feature
    :type id_: string
    :param text: the text to include with the tweet
    :type text: string
    :param image: the image to include with the tweet
    :type image: file-like object
    :param lon: Longitude (optional)
    :type lon: float
    :param lon: Latitude (optional)
    :type lon: float
    """

    log = get_logger(__name__)

    api = tweepy.API(get_auth(profile))

    with tempfile.NamedTemporaryFile(suffix=".jpg") as f:
        f.write(image.getbuffer())
        media = api.media_upload(f.name, file=f)

    status = api.update_status(text, media_ids=[media.media_id], lon=lon, lat=lat)

    profile.after_tweet(id_, status.id)

    log.info(
        f"Tweet sent for feature {id_} on profile {profile.id}, status id: {status.id}"
    )
