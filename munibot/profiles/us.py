import os
import pathlib
import sqlite3
import tempfile
from urllib.parse import urlencode

from osgeo import gdal, osr
import requests
from munibot.config import config
from munibot.profiles.base import BaseProfile


_TEMP_FILE_NAME = "countybot_us_tmp_file.tiff"


class CountyBotUS(BaseProfile):
    """
    A Munibot profile for posting images of US Couties
    """

    # Mandatory properties

    """
    A unique identifier for the profile, that will be used when running the
    commands and on the configuration file.
    """
    id = "us"

    """
    A longer description of the profile.
    """
    desc = "US Counties Bot (Orthoimagery The National Map)"

    # Mandatory hooks

    """
    Given a feature id, returns a tuple with the extent and the geometry of the
    the boundaries of the feature.

    The extent is a tuple containing (minx, miny, maxx, maxy). The geometry is
    a dict containing the geometry in GeoJSON format.
    """

    def get_boundaries(self, id_):

        base_url = "https://cartowfs.nationalmap.gov/arcgis/rest/services/govunits/MapServer/35/query"
        common_params = {
            "where": f"STCO_FIPSCODE='{id_}'",
            "f": "geojson",
        }

        geom_params = {
            "geometryType": "esriGeometryPolygon",
            "outFields": "STCO_FIPSCODE",
            "returnGeometry": "true",
            "geometryPrecision": "6",
        }

        r = requests.get(base_url, params=urlencode({**common_params, **geom_params}))

        try:
            feature_collection = r.json()
        except requests.exceptions.JSONDecodeError:
            raise ValueError(
                f"Error while querying geometry for county {id_}: {r.content}"
            )

        if "error" in feature_collection:
            raise ValueError(
                f"Error while querying geometry for county {id_}: {r.json()}"
            )

        geom = feature_collection["features"][0]["geometry"]

        extent_params = {
            "returnExtentOnly": "true",
        }

        r = requests.get(base_url, params=urlencode({**common_params, **extent_params}))

        extent = r.json()
        if "error" in extent:
            raise ValueError(
                f"Error while querying extent for county {id_}: {r.json()}"
            )

        bbox = extent["extent"]["bbox"]

        return bbox, geom

    """
    Returns a base image for the given extent (minx, miny, maxx, maxy).

    The return value is a file-like object containing the raster image for the
    provided extent.
    """

    def get_base_image(self, extent):

        bbox = self.extend_bbox(extent)

        wms_url = "https://basemap.nationalmap.gov/arcgis/services/USGSImageryOnly/MapServer/WMSServer"

        wms_options = {
            "url": wms_url,
            "layer": "0",
            "version": "1.3.0",
            "crs": "CRS:84",
            "bbox": bbox,
            "format": "image/geotiff",
        }
        img = self.get_wms_image(**wms_options)

#        if img.info().get("Content-Type") == "application/xml":
#            raise ValueError("Error retrieving WMS image: {}".format(img.read()))

        width, height = self.get_image_size(bbox)

        tmp_file_path = os.path.join(tempfile.gettempdir(), _TEMP_FILE_NAME)

        pathlib.Path(tmp_file_path).unlink(missing_ok=True)

        tmp_f = open(tmp_file_path, "w+b")

        self._geocode(tmp_f, img, bbox, width)

        return tmp_f

    """
    Returns the text that needs to be included in the post for this particular
    feature.
    """

    def _geocode(self, tmp_f_out, img, bounds, width=1500, crs=4326):

        with tempfile.NamedTemporaryFile() as tmp_f_in:

            tmp_f_in.write(img.read())

            # Opens source dataset
            src_ds = gdal.Open(tmp_f_in.name)
            driver = gdal.GetDriverByName("GTiff")

            # Open destination dataset
            dst_ds = driver.CreateCopy(tmp_f_out.name, src_ds, 0)

            minx = bounds[0]
            maxy = bounds[3]

            scalex = (bounds[2] - bounds[0]) / width

            gt = [minx, scalex, 0, maxy, 0, -scalex]

            # Set location
            dst_ds.SetGeoTransform(gt)

            # Get raster projection
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(crs)
            dest_wkt = srs.ExportToWkt()

            # Set projection
            dst_ds.SetProjection(dest_wkt)

            # Close file
            src_ds = None

    def get_text(self, id_):

        db = sqlite3.connect(config["db"]["path"])

        data = db.execute(
            """
            SELECT fullname, wikilink
            FROM us
            WHERE geoid = ?
            """,
            (id_,),
        )

        county_name, wiki_link = data.fetchone()

        return f"{county_name}\n\n\n{wiki_link}"

    """
    Returns the id of the next feature that should be posted.

    This is used if the ``munibot post`` command is called withot providing
    an id.
    """

    def get_next_id(self):

        db = sqlite3.connect(config["db"]["path"])

        id_ = db.execute(
            """
            SELECT geoid
            FROM us
            WHERE mastodon_us IS NULL
            ORDER BY RANDOM()
            LIMIT 1"""
        )

        return id_.fetchone()[0]

    # Optional hooks

    """
    Return a tuple with the longitude and latitude that should be associated
    with the post.

    The bot account should have location information on posts activated.
    """

    def get_lon_lat(self, id_):

        return None, None

    """
    Function that will be called after sending the post, that will receive
    the feature and the status id of the post sent.
    """

    def after_post(self, id_, status_id):

        db = sqlite3.connect(config["db"]["path"])

        db.execute(
            """
            UPDATE us
            SET mastodon_us = ?
            WHERE geoid = ?
            """,
            (
                status_id,
                id_,
            ),
        )

        db.commit()
