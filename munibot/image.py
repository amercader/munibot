import io
import time

import numpy
import rasterio
import rasterio.mask
import rasterio.plot
from PIL import Image

from .config import config, get_logger

MASK_OPACITY = 70


def get_mask(base_image, boundaries, nodata_value=0):
    """
    Returns an image mask for the base_image provided in the shape of the
    geometry of the boundaries provided.

    The base image and the boundaries geometry must share the same coordinate
    reference system.

    :param base_image: A file-like object with the image
    :type base_image: File-like object
    :param boundaries: a GeoJSON-like dict with the geometry of the boundaries
    :type boundaries: dict
    :param nodata_value: Numeric value that the base image has for NODATA values.
        Defaults to 0.
    :type nodata_value: int

    :returns: numpy-like array that can be transformed into an image
    """
    with rasterio.open(base_image) as base:
        out_raster, out_transform = rasterio.mask.mask(base, [boundaries])

        out_raster_bool = out_raster == nodata_value

        out_raster_int = out_raster_bool.astype(numpy.uint8)
        out_raster_int = out_raster_int * 255

        out_image_array = rasterio.plot.reshape_as_image(out_raster_int)

        return out_image_array


def process_image(base_image, mask_array, output_format="jpeg"):
    """
    Create the final image including the aerial imagery background with the
    outside of the featured boundaries masked.

    :param base_image: A file-like object with the image
    :type base_image: File-like object
    :param mask_array: numpy-like array that can be transformed into an image
    :type mask_array: array
    :param output_format: Output image format. Defaults to "jpeg".
    :type output_format: string

    :returns: resulting image saved as JPG
    :rtype: file-like object
    """

    mask = Image.fromarray(mask_array)
    mask_opacity = int(config["image"]["opacity"])

    alpha = int(mask_opacity * 255 / 100)
    mask.putalpha(alpha)

    pixels = mask.load()

    for x in range(mask.size[0]):
        for y in range(mask.size[1]):
            r, g, b, a = pixels[x, y]
            pixels[x, y] = (r, g, b, a if r == 255 else 0)

    back = Image.open(base_image)
    back.paste(mask, (0, 0), mask)

    out = io.BytesIO()

    back.save(out, format=output_format)

    return out


def create_image(profile, id_, output=None):
    """
    Creates the image to tweet for the provided profile and id

    :param profile: an instance of the profile class
    :type profile: object
    :param id_: the identifier of the feature to generate the image for
    :type id_: string
    :param output: Optional, image output path if provided the image will be
        saved as a JPG file in that location. If not (the default) a file-like
        object will be returned instead.
    :type output: string

    :returns: a file-like object with the generated image (or None
        if ``output`` is provided)
    :rtype: file-like object
    """

    log = get_logger(__name__)
    start = time.perf_counter()

    extent, boundaries = profile.get_boundaries(id_)
    log.debug("Received boundaries from profile ({})".format(extent))

    base_image = profile.get_base_image(extent)
    log.debug("Received base image from profile")

    nodata_value = getattr(profile, "image_nodata_value", 0)
    mask = get_mask(base_image, boundaries, nodata_value)
    log.debug("Image mask created")

    final_image = process_image(base_image, mask)

    end = time.perf_counter()
    log.info(f"Created image {id_}.jpg in {end - start:0.4f} seconds")

    if output:
        with open(output, "wb") as f:
            f.write(final_image.getbuffer())

    return final_image
