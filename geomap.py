#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 23:42:16 2019

@author: chris
"""

from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plot


class GeoMapImage:
    """
    Mapping - Pull tiles from a TileServer to create a map based on a lat/lon bounding box
    The primary output will be an image file ; containing the map details.

    Assuming OSM URL Formats
        tileserver.a.b.c/{z}/{x}/{y}.png

    Create a new GeoMap by calling

    geomap = GeoMap(tileserver=" ... ", lat_s, lat_n, lon_e, lon_w, zoom)
    """

    def __init__(self, tileserver, lat_s, lat_n, lon_e, lon_w, zoom):
        """
        Setup a GeoMap base image
        - tileserver = OSM Formatted URL Pattern
        -- tileserver.a.b.c/{z}/{x}/{y}.png
        - lat_s / lat_n = South and North Latitude boundaries
        - lon_e / lon_w = East and West Longitude boundaries
        """

        self.tileserver = tileserver
        self.bbox_south = lat_s
        self.bbox_north = lat_n
        self.bbox_east = lon_e
        self.bbox_west = lon_w
        if (zoom >= 1) and (zoom <= 19):
            self.zoom_level = zoom
        else:
            self.zoom_level = 16

        self.image_png = None
        self.base_image = None
        self.margin = 0.1

    def _create_tile_url(self, x_pos, y_pos, zoom_level):
        """Insert X / Y / Zoom into tileserver string"""
        return self.tileserver.format(z=zoom_level, x=x_pos, y=y_pos)

    def _image_to_png(self):
        """Use Bytes IO As target to write image to"""
        file = BytesIO()
        self.base_image.save(file, "png")
        file.name = "image.png"
        file.seek(0)
        img = file.read()
        self.image_png = img
        file.close()
        return img

    def get_png(self):
        """Convert the base image to a .png image"""
        result = None
        if not self.image_png is None:
            if not self.base_image is None:
                self.image_png = self._image_to_png()
                result = self.image_png
        else:
            result = self.image_png
        return result

    def draw_box(self, x1, y1, x2, y2):
        """
        Draw a box on the base image
        Return the updated image
        """
        result = True
        if x1 + x2 > y1 + y2:
            result = False
        return result

    def draw_spot(self, x1, y1):
        """
        Draw a circle on the base image
        Return the updated image
        """
