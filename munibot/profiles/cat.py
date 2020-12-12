import sqlite3
import urllib

from munibot.config import config

from .es import MuniBotEs


class MuniBotCat(MuniBotEs):

    id = "cat"

    desc = "Municipis Catalunya (Ortofoto ICGC)"

    image_nodata_value = 255

    def get_base_image(self, extent):

        bbox = (extent[1], extent[0], extent[3], extent[2])

        bbox = self.extend_bbox(bbox)

        wms_options = {
            "url": "https://geoserveis.icgc.cat/icc_ortohistorica/wms/service",
            "layer": "orto5m2016",
            "version": "1.1.1",
            "crs": "EPSG:4258",
            "bbox": bbox,
        }

        return self.get_wms_image(**wms_options)

    def get_next_id(self):

        db = sqlite3.connect(config["profile:cat"]["db_path"])

        id_ = db.execute(
            """
            SELECT natcode
            FROM munis_esp
            WHERE tweet_cat IS NULL
                AND codcomuni = '09'
            ORDER BY RANDOM()
            LIMIT 1"""
        )

        return id_.fetchone()[0]

    def get_text(self, id_):

        db = sqlite3.connect(config["profile:cat"]["db_path"])

        data = db.execute(
            """
            SELECT nameunit, namecomar
            FROM munis_esp
            WHERE natcode = ?
            """,
            (id_,),
        )

        name_muni, name_comarca = data.fetchone()

        wiki_link = "https://ca.wikipedia.org/wiki/{}".format(
            urllib.parse.quote(name_muni.replace(" ", "_"))
        )

        return f"{name_muni} ({name_comarca})\n\n\n{wiki_link}"

    def after_tweet(self, id_, status_id):

        db = sqlite3.connect(config["profile:cat"]["db_path"])

        db.execute(
            """
            UPDATE munis_esp
            SET tweet_cat = ?
            WHERE natcode = ?
            """,
            (
                status_id,
                id_,
            ),
        )

        db.commit()
