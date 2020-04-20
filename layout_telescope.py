"""
Telescope data class
- storage of telescope coordinates
- conversion between the different coordinate systems
"""
import math
from astropy import units as u
import pyproj


class TelescopeData:
    """
    data class for telescope IDs and
    positions
    """

    def __init__(self):
        """Inits TelescopeData with blah."""
        self.name = None
        self.x = math.nan * u.meter
        self.y = math.nan * u.meter
        self.z = math.nan * u.meter
        self.lon = math.nan * u.deg
        self.lat = math.nan * u.deg
        self.utm_east = math.nan * u.meter
        self.utm_north = math.nan * u.meter
        self.alt = math.nan * u.meter
        self.prod_id = {}

    def print_telescope(self):
        """
        print telescope name and positions
        """
        print("%s" % self.name)
        if not math.isnan(self.x.value) \
                and not math.isnan(self.y.value):
            print("\t x(->North): {0:0.2f} y(->West): {1:0.2f} z: {2:0.2f}"
                  .format(self.x, self.y, self.z))
        if not math.isnan(self.utm_east.value) \
                and not math.isnan(self.utm_north.value):
            print("\t UTM East: {0:0.2f} UTM North: {1:0.2f} Alt: {2:0.2f}"
                  .format(self.utm_east, self.utm_north, self.alt))
        if not math.isnan(self.lon.value) \
                and not math.isnan(self.lat.value):
            print("\t Longitude: {0:0.5f} Latitude: {1:0.5f}"
                  .format(self.lon, self.lat))
        if len(self.prod_id) > 0:
            print("\t", self.prod_id)

    def convert_local_to_mercator(self, crs_local, wgs84):
        """
        convert telescope position from local to mercator
        """
        if not crs_local or not wgs84:
            return

        if math.isnan(self.x.value) or math.isnan(self.y.value):
            return

        # calculate lon/lat
        if math.isnan(self.lon.value) or math.isnan(self.lat.value):
            self.lon, self.lat = u.deg * pyproj.transform(crs_local, wgs84,
                                                          self.x.value,
                                                          self.y.value)

    def convert_local_to_utm(self, crs_local, crs_utm):
        """
        convert telescope position from local to utm
        """
        if not crs_local or not crs_utm:
            return

        # calculate utms
        if math.isnan(self.utm_east.value) or math.isnan(self.utm_north.value):
            self.utm_east, self.utm_north = \
                u.meter * \
                pyproj.transform(crs_local, crs_utm,
                                 self.x.value, self.y.value)

    def convert_utm_to_mercator(self, crs_utm, wgs84):
        """
        convert telescope position from utm to mercator
        """
        if not crs_utm or not wgs84:
            return

        if not math.isnan(self.utm_east.value) \
                and not math.isnan(self.utm_north.value):
            return

        # calculate lon/lat
        if math.isnan(self.lon.value) \
                or math.isnan(self.lat.value):
            self.lon, self.lat = u.deg * \
                pyproj.transform(crs_utm, wgs84,
                                 self.utm_east.value,
                                 self.utm_north.value)

    def convert_utm_to_local(self, crs_utm, crs_local):
        """
        convert telescope position from utm to local
        """
        if not crs_utm or not crs_local:
            return

        if not math.isnan(self.utm_east.value) \
                and not math.isnan(self.utm_north.value):
            return

        if math.isnan(self.x.value) or math.isnan(self.y.value):
            self.x, self.y = u.meter * \
                pyproj.transform(crs_utm, crs_local,
                                 self.utm_east.value,
                                 self.utm_north.value)

    def convert_altitude(self, center_altitude):
        """
        convert telescope altitude to local or global
        """
        if not math.isnan(center_altitude.value):
            if math.isnan(self.z.value) and \
                    not math.isnan(self.alt.value):
                self.z = self.alt-center_altitude
            if math.isnan(self.alt.value) and \
                    not math.isnan(self.z.value):
                self.alt = self.z+center_altitude
