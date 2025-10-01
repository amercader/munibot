import re
import tempfile

from mastodon import Mastodon

from .config import config, get_logger


def get_client(profile):
    """
    Returns a Mastodon API instance using the access token for a
    particular profile.

    The returned instance can be used to interact with the Mastodon API using the
    profile bot account.
    """
    profile_config = config["profile:" + profile.id]

    mastodon = Mastodon(
        access_token=profile_config["mastodon_access_token"],
        api_base_url=profile_config["mastodon_api_base_url"],
    )

    return mastodon


def send_status(profile, id_, text, image, lon=None, lat=None):
    """
    Publish a new status in the profile bot account.

    Uploads the provided image and posts a new status with the text provided.

    After sending the status it calls the ``after_status()`` method of the provided
    profile, passing the feature id and the new status status id.

    :param profile: an instance of the profile class
    :type profile: object
    :param id_: the identifier of the feature
    :type id_: string
    :param text: the text to include with the status
    :type text: string
    :param image: the image to include with the status
    :type image: file-like object
    """
    log = get_logger(__name__)

    mastodon = get_client(profile)

    alt_text = re.sub(r'https?://\S+', '', text)
    alt_text = alt_text.strip()
    alt_text = f"An aerial image of {alt_text}"

    with tempfile.NamedTemporaryFile(suffix=".jpg") as f:
        f.write(image.getbuffer())
        media = mastodon.media_post(f.name, mime_type="image/jpeg", description=alt_text)

    status = mastodon.status_post(
        text, media_ids=[media["id"]], sensitive=False, visibility="public"
    )

    # Call the after_status method if it exists, otherwise fall back
    if hasattr(profile, "after_status"):
        profile.after_status(id_, status["id"])

    log.info(
        f"Status sent for feature {id_} on profile {profile.id}, status id: {status['id']}"
    )
