import io
import time

import numpy
import rasterio
import rasterio.mask
import rasterio.plot
from PIL import Image


from .config import config, load_profiles


MASK_OPACITY = 70


def get_mask(base_image, boundaries, nodata_value=0):

    with rasterio.open(base_image) as base:
        out_raster, out_transform = rasterio.mask.mask(base, [boundaries])

        out_raster_bool = out_raster == nodata_value

        out_raster_int = out_raster_bool.astype(numpy.uint8)
        out_raster_int = out_raster_int * 255

        out_image_array = rasterio.plot.reshape_as_image(out_raster_int)

        return out_image_array


def process_image(base_image, mask_array):

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

    back.save(out, format="jpeg")

    return out


def create_image(profile_name, id_):
    start = time.perf_counter()

    profiles = load_profiles()
    profile = profiles[profile_name]()

    extent, boundaries = profile.get_boundaries(id_)
    base_image = profile.get_base_image(extent)

    nodata_value = getattr(profile, "image_nodata_value", 0)
    mask = get_mask(base_image, boundaries, nodata_value)

    final_image = process_image(base_image, mask)

    with open("{}.jpg".format(id_), "wb") as f:
        f.write(final_image.getbuffer())

    end = time.perf_counter()
    print(f"Done. Created image {id_}.jpg in {end - start:0.4f} seconds")
