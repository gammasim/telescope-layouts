"""
Telescope data class
- storage of telescope coordinates
- conversion between the different coordinate systems
"""
import math
from astropy import units as u
import logging
import pyproj


class TelescopeData:
    """
    data class for telescope IDs and
    positions
    """

    def __init__(self):
        """Inits TelescopeData with blah."""
        self.name = None
        self.geo_code = None
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
        if self.geo_code:
            print("%s" % self.geo_code)
        if not math.isnan(self.x.value) and not math.isnan(self.y.value):
            print(
                "\t CORSIKA x(->North): {0:0.2f} y(->West): {1:0.2f} z: {2:0.2f}".format(
                    self.x, self.y, self.z
                )
            )
        if not math.isnan(self.utm_east.value) and not math.isnan(self.utm_north.value):
            print(
                "\t UTM East: {0:0.2f} UTM North: {1:0.2f} Alt: {2:0.2f}".format(
                    self.utm_east, self.utm_north, self.alt
                )
            )
        if not math.isnan(self.lon.value) and not math.isnan(self.lat.value):
            print(
                "\t Longitude: {0:0.5f} Latitude: {1:0.5f} Alt: {2:0.2f}".format(
                    self.lon, self.lat, self.alt
                )
            )
        if len(self.prod_id) > 0:
            print("\t", self.prod_id)

    def print_short_telescope_list(self, compact_coordinates):
        """
        print short list of telescope positions

        """
        if compact_coordinates == "eventdisplay":
            print(
                "{0} {1:10.2f} {2:10.2f}".format(
                    self.name, -1.0 * self.y.value, self.x.value
                )
            )
        elif compact_coordinates == "corsika":
            if self.geo_code:
                print(
                    "{0} {1:10.2f} {2:10.2f} {3:10.2f}   {4}".format(
                        self.name,
                        self.x.value,
                        self.y.value,
                        self.z.value,
                        self.geo_code,
                    )
                )
            else:
                print(
                    "{0} {1:10.2f} {2:10.2f} {3:10.2f}".format(
                        self.name, self.x.value, self.y.value, self.z.value
                    )
                )
        elif compact_coordinates == "utm":
            print(
                "{0} {1:10.2f} {2:10.2f} {3:10.2f}   {4}".format(
                    self.name,
                    self.utm_east.value,
                    self.utm_north.value,
                    self.alt.value,
                    self.geo_code,
                )
            )
        elif compact_coordinates == "mercator":
            print(
                "{0} {1:10.2f} {2:10.2f} {3:10.2f}".format(
                    self.name, self.lon.value, self.lat.value, self.alt.value
                )
            )

    def convert_local_to_mercator(self, crs_local, wgs84):
        """
        convert telescope position from local to mercator
        """

        # require valid coordinate systems
        if not crs_local or not wgs84:
            return

        # require valid position in local coordinates
        if math.isnan(self.x.value) or math.isnan(self.y.value):
            return

        # calculate lon/lat of a telescope
        if math.isnan(self.lon.value) or math.isnan(self.lat.value):

            transformer = pyproj.Transformer.from_crs(crs_local, wgs84)
            self.lat, self.lon = u.deg * transformer.transform(
                self.x.value, self.y.value
            )

    def convert_local_to_utm(self, crs_local, crs_utm):
        """
        convert telescope position from local to utm
        """

        # require valid coordinate systems
        if not crs_local or not crs_utm:
            return

        # require valid position in local coordinates
        if math.isnan(self.x.value) or math.isnan(self.y.value):
            return

        # calculate utms of a telescope
        if math.isnan(self.utm_east.value) or math.isnan(self.utm_north.value):
            transformer = pyproj.Transformer.from_crs(crs_local, crs_utm)
            self.utm_east, self.utm_north = u.meter * transformer.transform(
                self.x.value, self.y.value
            )

    def convert_utm_to_mercator(self, crs_utm, wgs84):
        """
        convert telescope position from utm to mercator
        """

        # require valid coordinate systems
        if not crs_utm or not wgs84:
            return

        # require valid position in UTM
        if math.isnan(self.utm_east.value) or math.isnan(self.utm_north.value):
            return

        # calculate lon/lat of a telescope
        if math.isnan(self.lon.value) or math.isnan(self.lat.value):
            transformer = pyproj.Transformer.from_crs(crs_utm, wgs84)
            self.lat, self.lon = u.deg * transformer.transform(
                self.utm_east.value, self.utm_north.value
            )

    def convert_utm_to_local(self, crs_utm, crs_local):
        """
        convert telescope position from utm to local
        """

        # require valid coordinate systems
        if not crs_utm or not crs_local:
            return

        # require valid position in UTM
        if math.isnan(self.utm_east.value) or math.isnan(self.utm_north.value):
            return

        if math.isnan(self.x.value) or math.isnan(self.y.value):
            transformer = pyproj.Transformer.from_crs(crs_utm, crs_local)
            self.x, self.y = u.meter * transformer.transform(
                self.utm_east.value, self.utm_north.value
            )

    def get_telescope_type(self, name):
        """
        guestimate telescope type from telescope name
        """
        if name[0:1] == "L":
            return "LST"
        elif name[0:1] == "M":
            return "MST"
        elif name[0:1] == "S":
            return "SST"
        return "CALIB"

    def convert_asl_to_corsika(self, corsika_obslevel, corsika_sphere_center):
        """
        convert telescope altitude to corsika
        """

        # require valid center altitude values
        if math.isnan(corsika_obslevel.value):
            return
        if math.isnan(self.z.value) and not math.isnan(self.alt.value):
            self.z = self.alt - corsika_obslevel
            try:
                self.z += corsika_sphere_center[self.get_telescope_type(self.name)]
            except KeyError:
                pass

    def convert_corsika_to_asl(self, corsika_obslevel, corsika_sphere_center):
        """
        convert corsika z to altitude
        """
        if not math.isnan(self.alt.value):
            return
        self.alt = corsika_obslevel + self.z
        try:
            self.alt -= corsika_sphere_center[self.get_telescope_type(self.name)]
        except KeyError:
            pass

    def convert(
        self,
        crs_local,
        wgs84,
        crs_utm,
        center_altitude,
        corsika_obslevel,
        corsika_sphere_center,
    ):
        """
        calculate telescope positions in missing coordinate
        systems
        """
        self.convert_local_to_mercator(crs_local, wgs84)
        self.convert_local_to_utm(crs_local, crs_utm)
        self.convert_utm_to_mercator(crs_utm, wgs84)
        self.convert_utm_to_local(crs_utm, crs_local)

        self.convert_asl_to_corsika(corsika_obslevel, corsika_sphere_center)
        self.convert_corsika_to_asl(corsika_obslevel, corsika_sphere_center)
