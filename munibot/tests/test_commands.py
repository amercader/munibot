import sys
from unittest import mock

import pytest

from munibot.munibot import main


class MockProfile:

    id = None

    def get_text(self, id_):
        return f"Test text {self.id}"

    def get_next_id(self):
        return "abc"

    def get_lon_lat(self, id_):
        return 1.2781, 41.1202


class MockProfileEs(MockProfile):
    id = "es"


class MockProfileCat(MockProfile):
    id = "cat"


mock_profiles = {
    "es": MockProfileEs,
    "cat": MockProfileCat,
}


def test_ini_file_not_found():

    command = ["munibot", "create", "es", "-c", "notfound.ini"]
    with mock.patch.object(sys, "argv", command):
        with pytest.raises(SystemExit) as m:
            main()
    assert m.value.code == 1


def test_unknown_profile():

    command = ["munibot", "create", "nope"]
    with mock.patch.object(sys, "argv", command):
        with pytest.raises(SystemExit) as m:
            main()
    assert m.value.code == 1


def test_create():

    command = ["munibot", "create", "cat"]
    with mock.patch.object(sys, "argv", command):
        with mock.patch("munibot.munibot.load_profiles", return_value=mock_profiles):
            with mock.patch("munibot.munibot.create_image") as m:
                main()

    assert isinstance(m.call_args[0][0], MockProfileCat)

    assert m.call_args[0][1] == "abc"

    assert m.call_args[0][2] == m.call_args[0][1] + ".jpg"


def test_create_passing_id():

    command = ["munibot", "create", "es", "-i", "xyz"]
    with mock.patch.object(sys, "argv", command):
        with mock.patch("munibot.munibot.load_profiles", return_value=mock_profiles):
            with mock.patch("munibot.munibot.create_image") as m:
                main()

    assert isinstance(m.call_args[0][0], MockProfileEs)

    assert m.call_args[0][1] == "xyz"

    assert m.call_args[0][2] == "xyz.jpg"


def test_create_passing_output():

    command = ["munibot", "create", "es", "-o", "/tmp/"]
    with mock.patch.object(sys, "argv", command):
        with mock.patch("munibot.munibot.load_profiles", return_value=mock_profiles):
            with mock.patch("munibot.munibot.create_image") as m:
                main()

    assert isinstance(m.call_args[0][0], MockProfileEs)

    assert m.call_args[0][1] == "abc"

    assert m.call_args[0][2] == "/tmp/abc.jpg"


def test_post():

    command = ["munibot", "post", "cat"]
    with mock.patch.object(sys, "argv", command):
        with mock.patch("munibot.munibot.load_profiles", return_value=mock_profiles):
            with mock.patch(
                "munibot.munibot.create_image", return_value="created_image"
            ) as m:
                with mock.patch("munibot.munibot.send_status") as m:
                    main()

    assert isinstance(m.call_args[0][0], MockProfileCat)

    assert m.call_args[0][1] == "abc"

    assert m.call_args[0][2] == "Test text cat"
    assert m.call_args[0][3] == "created_image"

    assert m.call_args[0][4] == 1.2781
    assert m.call_args[0][5] == 41.1202
