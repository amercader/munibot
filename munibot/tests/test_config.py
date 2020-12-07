import pytest

from munibot.config import load_config, load_profiles, config


@pytest.mark.usefixtures("load_config")
def test_load_config():

    assert config["twitter"]["api_key"] == "CHANGE_ME"
    assert config["twitter"]["api_key_secret"] == "CHANGE_ME_SECRET"

    assert int(config["image"]["opacity"]) == 70
    assert int(config["image"]["max_pixel_side"]) == 1500

    assert config["profile:test"]["twitter_access_token"] == "CHANGE_ME_PROFILE"
    assert (
        config["profile:test"]["twitter_access_token_secret"]
        == "CHANGE_ME_PROFILE_SECRET"
    )


def test_config_path_not_found():

    with pytest.raises(ValueError):
        load_config("not_found.ini")


def test_load_profiles():

    assert sorted(load_profiles().keys()) == sorted(["es", "cat"])
