import os
import pathlib

import pytest
import fiona

from munibot.profiles.base import BaseProfile
from munibot.config import load_config as main_load_config


@pytest.fixture
def load_config():
    test_ini_path = os.path.join(
        pathlib.Path(__file__).parent.absolute(), "munibot.test.ini"
    )
    main_load_config(test_ini_path)


path = pathlib.Path(__file__).parent.absolute()


def _test_image_path():
    """
    A 100 x 50 pixel GeoTIFF image, with 0 as NODATA value
    """
    return os.path.join(path, "test.tiff")


def _test_boundaries_path():
    """
    A GeoJSON feature covering the center of the image and leaving
    3 px on each side uncovered
    """
    return os.path.join(path, "test.geojson")


@pytest.fixture
def test_image_path():
    return _test_image_path()


@pytest.fixture
def test_boundaries_path():
    return _test_boundaries_path()


class MuniBotTest(BaseProfile):

    id = "test"

    desc = "A test profile to run tests"

    image_nodata_value = 0

    def get_boundaries(self, id_):
        with fiona.open(_test_boundaries_path(), "r") as src:
            geometry = [f["geometry"] for f in src][0]
            return src.bounds, geometry

    def get_base_image(self, extent):
        return open(_test_image_path(), "rb")

    def get_text(self, id_):
        return "Test feature (tweet text)"

    def get_next_id(self):
        return "1234"

    def get_lon_lat(self, id_):
        return 1.2781, 41.1202


@pytest.fixture
def test_profile():
    return MuniBotTest()
