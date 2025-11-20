import sqlite3
import urllib

from munibot.config import config

from .es import MuniBotEs


class MuniBotCat(MuniBotEs):

    id = "cat"

    desc = "Municipis Catalunya (Ortofoto ICGC)"

    image_nodata_value = 0

    def get_base_image(self, extent):

        bbox = self.extend_bbox(extent)

        wms_options = {
            "url": "https://geoserveis.icgc.cat/servei/catalunya/orto-territorial/wms",
            "layer": "ortofoto_color_vigent",
            "version": "1.3.0",
            "crs": "EPSG:4258",
            "bbox": bbox,
        }

        return self.get_wms_image(**wms_options)

    def get_next_id(self):

        db = sqlite3.connect(config["db"]["path"])

        id_ = db.execute(
            """
            SELECT natcode
            FROM es
            WHERE mastodon_cat IS NULL
                AND codcomuni = '09'
            ORDER BY RANDOM()
            LIMIT 1"""
        )

        return id_.fetchone()[0]

    def get_text(self, id_):

        db = sqlite3.connect(config["db"]["path"])

        data = db.execute(
            """
            SELECT nameunit, namecomar
            FROM es
            WHERE natcode = ?
            """,
            (id_,),
        )

        name_muni, name_comarca = data.fetchone()

        wiki_link = "https://ca.wikipedia.org/wiki/{}".format(
            urllib.parse.quote(name_muni.replace(" ", "_"))
        )

        return f"{name_muni} ({name_comarca})\n\n\n{wiki_link}"

    def after_post(self, id_, status_id):

        db = sqlite3.connect(config["db"]["path"])

        db.execute(
            """
            UPDATE es
            SET mastodon_cat = ?
            WHERE natcode = ?
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
            SELECT cod_ine, mastodon_cat
            FROM es
            WHERE mastodon_cat IS NOT NULL
            """
        posts_query = db.execute(sql)

        posts = {row[0]: row[1] for row in posts_query.fetchall()}

        count = db.execute("SELECT COUNT(*) FROM es WHERE codcomuni = '09'").fetchone()[0]

        return count, posts
