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
