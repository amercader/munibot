import pytest
from numpy.testing import assert_array_equal

import fiona
from PIL import Image

from munibot.image import get_mask, process_image, create_image


def test_get_mask(test_boundaries_path, test_image_path):
    """
    Our image is 100 x 50 pixels, and the GeoJSON boundaries should leave
    3px on each side. As the default NODATA value is 0, we expect a mask like:

    255 255 255 255 255 [...] 255 255 255 255 255
    255 255 255 255 255 [...] 255 255 255 255 255
    255 255 255 255 255 [...] 255 255 255 255 255
    255 255 255  0   0  [...]  0   0  255 255 255
    255 255 255  0   0  [...]  0   0  255 255 255
    255 255 255  0   0  [...]  0   0  255 255 255
    [...]
    255 255 255  0   0  [...]  0   0  255 255 255
    255 255 255  0   0  [...]  0   0  255 255 255
    255 255 255  0   0  [...]  0   0  255 255 255
    255 255 255 255 255 [...] 255 255 255 255 255
    255 255 255 255 255 [...] 255 255 255 255 255
    255 255 255 255 255 [...] 255 255 255 255 255
    """

    with fiona.open(test_boundaries_path, "r") as src:
        boundaries = [f["geometry"] for f in src][0]

    base_image = open(test_image_path, "rb")

    mask = get_mask(base_image, boundaries)

    base_image.close()

    # Top
    assert_array_equal(mask[0][50], (255, 255, 255))
    assert_array_equal(mask[1][50], (255, 255, 255))
    assert_array_equal(mask[2][50], (255, 255, 255))
    assert_array_equal(mask[3][50], (0, 0, 0))

    # Bottom
    assert_array_equal(mask[46][50], (0, 0, 0))
    assert_array_equal(mask[47][50], (255, 255, 255))
    assert_array_equal(mask[48][50], (255, 255, 255))
    assert_array_equal(mask[49][50], (255, 255, 255))

    # Left
    assert_array_equal(mask[25][0], (255, 255, 255))
    assert_array_equal(mask[25][1], (255, 255, 255))
    assert_array_equal(mask[25][2], (255, 255, 255))
    assert_array_equal(mask[25][3], (0, 0, 0))

    # Right
    assert_array_equal(mask[25][96], (0, 0, 0))
    assert_array_equal(mask[25][97], (255, 255, 255))
    assert_array_equal(mask[25][98], (255, 255, 255))
    assert_array_equal(mask[25][99], (255, 255, 255))


@pytest.mark.usefixtures("load_config")
def test_process_image(test_boundaries_path, test_image_path):
    with fiona.open(test_boundaries_path, "r") as src:
        boundaries = [f["geometry"] for f in src][0]

    base_image = open(test_image_path, "rb")

    mask = get_mask(base_image, boundaries)

    final_image = process_image(base_image, mask, output_format="tiff")

    base = Image.open(base_image)
    base_pixels = base.load()

    final = Image.open(final_image)
    final_pixels = final.load()

    # Top
    assert base_pixels[50, 0] != final_pixels[50, 0]
    assert base_pixels[50, 1] != final_pixels[50, 1]
    assert base_pixels[50, 2] != final_pixels[50, 2]
    assert base_pixels[50, 3] == final_pixels[50, 3]

    # Bottom
    assert base_pixels[50, 46] == final_pixels[50, 46]
    assert base_pixels[50, 47] != final_pixels[50, 47]
    assert base_pixels[50, 48] != final_pixels[50, 48]
    assert base_pixels[50, 49] != final_pixels[50, 49]

    # Left
    assert base_pixels[0, 25] != final_pixels[0, 25]
    assert base_pixels[1, 25] != final_pixels[1, 25]
    assert base_pixels[2, 25] != final_pixels[2, 25]
    assert base_pixels[3, 25] == final_pixels[3, 25]

    # Right
    assert base_pixels[96, 25] == final_pixels[96, 25]
    assert base_pixels[97, 25] != final_pixels[97, 25]
    assert base_pixels[98, 25] != final_pixels[98, 25]
    assert base_pixels[99, 25] != final_pixels[99, 25]


def test_create_image(test_profile):

    image_io = create_image(test_profile, "xyz")

    image = Image.open(image_io)

    assert image.size == (100, 50)
