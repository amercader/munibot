import pytest

from munibot.config import config, load_config, load_profiles


@pytest.mark.usefixtures("load_config")
def test_load_config():

    assert int(config["image"]["opacity"]) == 70
    assert int(config["image"]["max_pixel_side"]) == 1500

    assert config["profile:test"]["mastodon_access_token"] == "CHANGE_ME"
    assert config["profile:test"]["mastodon_api_base_url"] == "CHANGE_ME_URL"


def test_config_path_not_found():

    with pytest.raises(ValueError):
        load_config("not_found.ini")


def test_load_profiles():

    assert sorted(load_profiles().keys()) == sorted(["es", "cat"])
