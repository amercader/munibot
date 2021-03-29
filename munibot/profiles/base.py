import shapely.geometry
from owslib.wms import WebMapService

from munibot.config import config


class BaseProfile:
    """
    Base profile class that all profile bot classes should inherit from.

    Contains mandatory hooks that all profiles need to implement, optional
    hooks and utility methods.
    """

    # Mandatory properties

    """
    A unique identifier for the profile, that will be used when running the
    commands and on the configuration file.
    """
    id = None

    """
    A longer description of the profile.
    """
    desc = None

    # Optional properties

    """
    Value that NODATA pixels have in the base image. Usually 0 or 255.
    """
    image_nodata_value = 0

    # Mandatory hooks

    """
    Given a feature id, returns a tuple with the extent and the geometry of the
    the boundaries of the feature.

    The extent is a tuple containing (minx, miny, maxx, maxy). The geometry is a
    dict containing the geometry in GeoJSON format.
    """

    def get_boundaries(self, id_):

        raise NotImplementedError

    """
    Returns a base image for the given extent (minx, miny, maxx, maxy).

    The return value is a file-like object containing the raster image for the
    provided extent.
    """

    def get_base_image(self, extent):

        raise NotImplementedError

    """
    Returns the text that needs to be included in the tweet for this particular
    feature.
    """

    def get_text(self, id_):

        raise NotImplementedError

    """
    Returns the id of the next feature that should be tweeted.

    This is used if the ``munibot tweet`` command is called withot providing
    an id.
    """

    def get_next_id(self):

        raise NotImplementedError

    # Optional hooks

    """
    Return a tuple with the longitude and latitude that should be associated
    with the tweet.

    The bot account should have location information on tweets activated.
    """

    def get_lon_lat(self, id_):

        return None, None

    """
    Function that will be called after sending the tweet, that will receive
    the feature and the status id of the tweet sent.
    """

    def after_tweet(self, id_, status_id):

        pass

    # Internal

    def __init__(self):
        if not self.id or not self.desc:
            class_name = self.__class__.__name__
            raise NotImplementedError(
                f'Profile class {class_name} must define the "id" and "desc" properties'
            )

    # Utilities

    """
    Returns the vertical and horizontal distance of the provided bounding box.
    """

    def get_bbox_distances(self, bbox):
        dx = abs(bbox[0] - bbox[2])
        dy = abs(bbox[1] - bbox[3])

        return dx, dy

    """
    Calculates the image size based on the bounding box provided and
    the ``max_pixel_side`` configuration option.
    """

    def get_image_size(self, bbox):

        dx, dy = self.get_bbox_distances(bbox)

        max_pixel_side = int(config["image"]["max_pixel_side"])

        if dx > dy:
            return (max_pixel_side, max_pixel_side * dy / dx)
        else:
            return (max_pixel_side * dx / dy, max_pixel_side)

    """
    Extends the bounding box to include a buffer zone around it.
    """

    def extend_bbox(self, bbox):

        dx, dy = self.get_bbox_distances(bbox)

        distance = dx * 0.1 if dx > dy else dy * 0.1
        return shapely.geometry.box(*bbox).buffer(distance).bounds

    """
    Helper function to request a WMS image.

    Returns a file-like object with the requested image.
    """

    def get_wms_image(
        self,
        url,
        layer,
        bbox,
        crs,
        version="1.3.0",
        styles=None,
        format="image/tiff",
        headers=None
    ):

        wms = WebMapService(url, version=version, headers=headers)

        img = wms.getmap(
            layers=[layer],
            srs=crs,
            styles=styles,
            bbox=bbox,
            size=self.get_image_size(bbox),
            format=format,
        )

        return img
