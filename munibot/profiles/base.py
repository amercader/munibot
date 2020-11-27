import shapely.geometry
from owslib.wms import WebMapService

from munibot.config import config


class BaseProfile(object):
    def get_bbox_distances(self, bbox):
        dx = abs(bbox[0] - bbox[2])
        dy = abs(bbox[1] - bbox[3])

        return dx, dy

    def get_image_size(self, bbox):

        dx, dy = self.get_bbox_distances(bbox)

        max_pixel_side = int(config["image"]["max_pixel_side"])

        if dx > dy:
            return (max_pixel_side, max_pixel_side * dy / dx)
        else:
            return (max_pixel_side * dx / dy, max_pixel_side)

    def extend_bbox(self, bbox):

        dx, dy = self.get_bbox_distances(bbox)

        distance = dx * 0.1 if dx > dy else dy * 0.1
        return shapely.geometry.box(*bbox).buffer(distance).bounds

    def get_wms_image(
        self,
        url,
        layer,
        bbox,
        crs,
        version="1.3.0",
        styles=["default"],
        format="image/tiff",
    ):

        wms = WebMapService(url, version=version)

        img = wms.getmap(
            layers=[layer],
            srs=crs,
            styles=styles,
            bbox=bbox,
            size=self.get_image_size(bbox),
            format=format,
        )

        return img
