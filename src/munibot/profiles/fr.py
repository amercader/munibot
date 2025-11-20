import sqlite3
import urllib

import requests
from munibot.config import config
from munibot.profiles.base import BaseProfile


class CommuneBotFr(BaseProfile):
    """
    A Munibot profile for posting images of French communes
    """

    # Mandatory properties

    """
    A unique identifier for the profile, that will be used when running the
    commands and on the configuration file.
    """
    id = "fr"

    """
    A longer description of the profile.
    """
    desc = "Communes de France (Orthophoto IGN)"

    image_nodata_value = 255

    # Mandatory hooks

    """
    Given a feature id, returns a tuple with the extent and the geometry of the
    the boundaries of the feature.

    The extent is a tuple containing (minx, miny, maxx, maxy). The geometry is
    a dict containing the geometry in GeoJSON format.
    """

    def get_boundaries(self, id_):

        cadastre_url = "https://apicarto.ign.fr/api/cadastre/commune"

        params = {"code_insee": id_}

        r = requests.get(cadastre_url, params=params)

        feature_collection = r.json()

        try:
            bbox = feature_collection["bbox"]
        except KeyError:
            raise ValueError(f"No geometry returned for commune {id_}")

        extent = (
            bbox[0],
            bbox[2],
            bbox[1],
            bbox[3],
        )

        geom = feature_collection["features"][0]["geometry"]

        return (extent, geom)

    """
    Returns a base image for the given extent (minx, miny, maxx, maxy).

    The return value is a file-like object containing the raster image for the
    provided extent.
    """

    def get_base_image(self, extent):

        bbox = (extent[0], extent[2], extent[1], extent[3])

        bbox = self.extend_bbox(bbox)

        crs = self._get_crs(bbox)

        # wms_url = "https://wxs.ign.fr/essentiels/geoportail/r/wms"
        wms_url = "https://data.geopf.fr/wms-r/wms"

        headers = {"User-Agent": "munibot-fr"}

        wms_options = {
            "url": wms_url,
            "layer": "ORTHOIMAGERY.ORTHOPHOTOS",
            "version": "1.3.0",
            "crs": crs,
            "bbox": bbox,
            "format": "image/geotiff",
            "headers": headers,
        }

        img = self.get_wms_image(**wms_options)

        # if img.info().get("Content-Type") == "application/xml":
        #    raise ValueError("Error retrieving WMS image: {}".format(img.read()))

        return img

    """
    Returns the text that needs to be included in the post for this particular
    feature.
    """

    def get_text(self, id_):

        db = sqlite3.connect(config["db"]["path"])

        data = db.execute(
            """
            SELECT nom, nom_departement
            FROM fr
            WHERE insee = ?
            """,
            (id_,),
        )

        name_commune, name_dep = data.fetchone()

        wiki_link = "https://fr.wikipedia.org/wiki/{}".format(
            urllib.parse.quote(name_commune.replace(" ", "_"))
        )

        return f"{name_commune} ({name_dep})\n\n\n{wiki_link}"

        raise NotImplementedError

    """
    Returns the id of the next feature that should be posted.

    This is used if the ``munibot post`` command is called withot providing
    an id.
    """

    def get_next_id(self):

        db = sqlite3.connect(config["db"]["path"])

        id_ = db.execute(
            """
            SELECT insee
            FROM fr
            WHERE mastodon_fr IS NULL
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

        db = sqlite3.connect(config["db"]["path"])

        data = db.execute(
            """
            SELECT lon, lat
            FROM fr
            WHERE insee = ?
            """,
            (id_,),
        )

        lon, lat = data.fetchone()

        return lon, lat

    """
    Function that will be called after sending the post, that will receive
    the feature and the status id of the post sent.
    """

    def after_post(self, id_, status_id):

        db = sqlite3.connect(config["db"]["path"])

        db.execute(
            """
            UPDATE fr
            SET mastodon_fr = ?
            WHERE insee = ?
            """,
            (
                status_id,
                id_,
            ),
        )

        db.commit()

    def posts_dump(self):

        db = sqlite3.connect(config["db"]["path"])

        sql = """
            SELECT insee, mastodon_fr
            FROM fr
            WHERE mastodon_fr IS NOT NULL
            """
        posts_query = db.execute(sql)

        posts = {row[0]: row[1] for row in posts_query.fetchall()}

        count = db.execute("SELECT COUNT(*) FROM fr").fetchone()[0]

        return count, posts

    # Internal methods

    def _get_crs(self, bbox):

        # YOLO
        outre_mer = bbox[0] < -7.30 or bbox[2] > 11 or bbox[1] < 39 or bbox[3] > 52

        return "CRS:84" if outre_mer else "EPSG:4258"
