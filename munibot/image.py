import argparse
import io
import time
import xml.etree.ElementTree as ET

import fiona
import numpy
import rasterio
import rasterio.mask
import rasterio.plot
import shapely.geometry
from owslib.wfs import WebFeatureService
from owslib.wms import WebMapService
from PIL import Image

bbox = (
    -0.3143861210000000,
    42.6773988290000048,
    -0.1778259840000000,
    42.8078972170000043,
)

pnoa_wms_url = "http://www.ign.es/wms-inspire/pnoa-ma"

layer = "OI.OrthoimageCoverage"

admin_wfs = "https://www.ign.es/wfs-inspire/unidades-administrativas"

MASK_OPACITY = 70

MAX_PIXEL_SIDE = 1500


def get_bbox_distances(bbox):
    dx = abs(bbox[0] - bbox[2])
    dy = abs(bbox[1] - bbox[3])

    return dx, dy


def get_image_size(bbox):

    dx, dy = get_bbox_distances(bbox)

    if dx > dy:
        return (MAX_PIXEL_SIDE, MAX_PIXEL_SIDE * dy / dx)
    else:
        return (MAX_PIXEL_SIDE * dx / dy, MAX_PIXEL_SIDE)


def extend_bbox(bbox):

    dx, dy = get_bbox_distances(bbox)

    distance = dx * 0.1 if dx > dy else dy * 0.1
    return shapely.geometry.box(*bbox).buffer(distance).bounds


def get_base_image(extent):
    wms = WebMapService(pnoa_wms_url, version="1.3.0")
    #    icgc_wms_url = 'https://geoserveis.icgc.cat/icc_ortohistorica/wms/service'
    #    layer = 'orto5m2016'
    #    wms = WebMapService(icgc_wms_url, version="1.1.1")

    bbox = (extent[1], extent[0], extent[3], extent[2])

    bbox = extend_bbox(bbox)

    img = wms.getmap(
        layers=[layer],
        srs="EPSG:4258",
        styles=["default"],
        bbox=bbox,
        size=get_image_size(bbox),
        format="image/tiff",
    )

    return img


def get_boundaries(id_):

    wfs = WebFeatureService(admin_wfs, version="2.0.0")

    typename = "au:AdministrativeUnit"

    response = wfs.getfeature(
        storedQueryID="urn:ogc:def:query:OGC-WFS::GetFeatureById",
        storedQueryParams={"ID": "AU_ADMINISTRATIVEUNIT_{}".format(id_)},
    )

    root = ET.fromstring(response.read())
    ns = {"au": "http://inspire.ec.europa.eu/schemas/au/4.0"}

    gml_geometry_element = [e for e in root.find("au:geometry", ns)][0]
    gml_geometry = ET.tostring(gml_geometry_element)

    gml = """
    <gml:FeatureCollection xmlns:gml="http://www.opengis.net/gml/3.2">
        <gml:featureMember>
          <gml:geometry>
            {geometry}
          </gml:geometry>
        </gml:featureMember>
    </gml:FeatureCollection>
    """.format(
        geometry=gml_geometry.decode("utf8")
    ).strip()

    gml_f = io.BytesIO(gml.encode("utf8"))
    with fiona.open(gml_f, "r") as src:
        geometry = [f["geometry"] for f in src][0]

        return src.bounds, geometry


def get_mask(base_image, boundaries, nodata_value=0):

    with rasterio.open(base_image) as base:
        out_raster, out_transform = rasterio.mask.mask(base, [boundaries])

        out_raster_bool = out_raster == 0

        out_raster_int = out_raster_bool.astype(numpy.uint8)
        out_raster_int = out_raster_int * 255

        out_image_array = rasterio.plot.reshape_as_image(out_raster_int)

        return out_image_array


def process_image(base_image, mask_array, mask_opacity=MASK_OPACITY):

    mask = Image.fromarray(mask_array)
    mask.save("masktarragona_ign.jpg")

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


def create_image(id_):
    start = time.perf_counter()

    extent, boundaries = get_boundaries(id_)
    base_image = get_base_image(extent)
    mask = get_mask(base_image, boundaries)

    final_image = process_image(base_image, mask)

    with open("{}.jpg".format(id_), "wb") as f:
        f.write(final_image.getbuffer())

    end = time.perf_counter()
    print(f"Done. Created image {id_}.jpg in {end - start:0.4f} seconds")
