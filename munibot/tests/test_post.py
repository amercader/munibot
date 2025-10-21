from unittest import mock

import pytest

from munibot.image import create_image
from munibot.mastodon import get_client, send_status


@pytest.mark.usefixtures("load_config")
def test_get_client(test_profile):

    auth = get_client(test_profile)

    assert auth.access_token == "CHANGE_ME"
    assert auth.api_base_url == "https://CHANGE_ME_URL"


class MockMastodonAPI:
    def media_post(self, *args, **kwargs):

        return {"id": "media_xyz"}

    def status_post(self, *args, **kwargs):

        return {"id": "status_xyz"}


@pytest.mark.usefixtures("load_config")
def test_send_tweet(test_profile):

    id_ = test_profile.get_next_id()
    text = test_profile.get_text(id_)
    image = create_image(test_profile, id_)
    lon, lat = test_profile.get_lon_lat(id_)

    test_profile.after_post = mock.MagicMock()

    with mock.patch("munibot.mastodon.Mastodon") as m:
        m.return_value=MockMastodonAPI()
        send_status(test_profile, id_, text, image, lon, lat)
    test_profile.after_post.assert_called_once_with("1234", "status_xyz")
