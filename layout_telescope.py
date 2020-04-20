import math
from astropy import units as u


class telescopeData:
    """
    data class for telescope IDs and
    positions
    """

    def __init__(self):
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
