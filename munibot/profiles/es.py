import io
import xml.etree.ElementTree as ET

from owslib.wfs import WebFeatureService
from owslib.wms import WebMapService

import fiona

from .base import BaseProfile


class MuniBotEs(BaseProfile):

    id = "es"

    desc = "Municipios España (Ortofoto PNOA)"

    image_nodata_value = 0

    def get_base_image(self, extent):

        bbox = (extent[1], extent[0], extent[3], extent[2])

        bbox = self.extend_bbox(bbox)

        wms_options = {
            "url": "http://www.ign.es/wms-inspire/pnoa-ma",
            "layer": "OI.OrthoimageCoverage",
            "version": "1.3.0",
            "crs": "EPSG:4258",
            "bbox": bbox,
        }

        return self.get_wms_image(**wms_options)

    def get_boundaries(self, id_):

        admin_wfs = "https://contenido.ign.es/wfs-inspire/unidades-administrativas"

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
