from unittest import mock

import pytest

from munibot.image import create_image
from munibot.tweet import get_auth, get_verify_auth, send_tweet


@pytest.mark.usefixtures("load_config")
def test_get_verify_auth():

    auth = get_verify_auth()

    assert auth.access_token =="oob"
    assert auth.access_token_secret is None

    assert auth.consumer_key == "CHANGE_ME"
    assert auth.consumer_secret == "CHANGE_ME_SECRET"


@pytest.mark.usefixtures("load_config")
def test_get_auth(test_profile):

    auth = get_auth(test_profile)

    assert auth.access_token == "CHANGE_ME_PROFILE"
    assert auth.access_token_secret == "CHANGE_ME_PROFILE_SECRET"

    assert auth.consumer_key == "CHANGE_ME"
    assert auth.consumer_secret == "CHANGE_ME_SECRET"


class MockTweepyAPI:
    def media_upload(self, file_name, file):
        class Media:
            media_id = "media_xyz"

        return Media()

    def update_status(self, text, media_ids, lon, lat):
        class Status:
            id = "status_xyz"

        return Status()


@pytest.mark.usefixtures("load_config")
def test_send_tweet(test_profile):

    id_ = test_profile.get_next_id()
    text = test_profile.get_text(id_)
    image = create_image(test_profile, id_)
    lon, lat = test_profile.get_lon_lat(id_)

    test_profile.after_tweet = mock.MagicMock()

    with mock.patch("munibot.tweet.tweepy") as m:
        m.API = mock.MagicMock(return_value=MockTweepyAPI())
        send_tweet(test_profile, id_, text, image, lon, lat)
    test_profile.after_tweet.assert_called_once_with("1234", "status_xyz")
