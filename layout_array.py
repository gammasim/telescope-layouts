"""
arrayData class descripe an array of telescopes
"""

import math
from astropy.table import Table
from astropy import units as u
import pyproj

import layout_telescope


class ArrayData:
    """
    layout class for
    - storage of telescope position
    - conversion of coordinate systems of positions
    """

    def __init__(self, verbose_debug = True):
        """Inits ArrayData with blah."""
        self.name = None
        self.telescope_list = []
        # centre of the array
        self.epsg = math.nan
        self.center_northing = math.nan*u.meter
        self.center_easting = math.nan*u.meter
        self.center_lon = None
        self.center_lat = None
        self.center_altitude = math.nan*u.meter
        self.verbose = verbose_debug


    def read_telescope_list(self, telescope_file):
        """
        read list of telescopes from a ecsv file
        """
        try:
            table = Table.read(telescope_file, format='ascii.ecsv')
        except Exception as ex:
            print('Error reading telescope list from ', telescope_file)
            print(ex.args)
            return False
        if self.verbose:
            print(table.meta)
            print(table)
        print("reading telescope list from ", telescope_file)
        # require telescope_name in telescope lists
        if 'telescope_name' not in table.colnames:
            print('Error reading telescope list from ', telescope_file)
            print('   required column telescope_name missing')
            print(table.meta)
            return False
        # reference coordinate system
        if 'EPSG' in table.meta:
            self.epsg = table.meta['EPSG']
        if 'center_northing' in table.meta and \
                'center_easting' in table.meta:
            self.center_northing = u.Quantity(table.meta['center_northing'])
            self.center_easting = u.Quantity(table.meta['center_easting'])
        if 'center_lon' in table.meta and \
                'center_lat' in table.meta:
            self.center_lon = u.Quantity(table.meta['center_lon'])
            self.center_lat = u.Quantity(table.meta['center_lat'])
        if 'center_alt' in table.meta:
            self.center_altitude = u.Quantity(table.meta['center_alt'])
        # initialise telescope lists from productions
        prod_list = []
        for row_name in table.colnames:
            if row_name.find("prod") >= 0:
                prod_list.append(row_name)

        for row in table:
            tel = layout_telescope.TelescopeData()
            tel.name = row['telescope_name']
            if 'pos_x' in table.colnames:
                # TMPTMP
                tel.y = -1.*row['pos_x']*table['pos_x'].unit
            if 'pos_y' in table.colnames:
                # TMPTMP
                tel.x = row['pos_y']*table['pos_y'].unit
            if 'pos_z' in table.colnames:
                tel.z = row['pos_z']*table['pos_z'].unit
            if 'utm_east' in table.colnames:
                tel.utm_east = row['utm_east']*table['utm_east'].unit
            if 'utm_north' in table.colnames:
                tel.utm_north = row['utm_north']*table['utm_north'].unit
            if 'alt' in table.colnames:
                tel.alt = row['alt']*table['alt'].unit
            if 'lon' in table.colnames:
                tel.lon = row['lon']*table['lon'].unit
            if 'lat' in table.colnames:
                tel.utm_north = row['lat']*table['lat'].unit

            for prod in prod_list:
                tel.prod_id[prod] = row[prod]

            self.telescope_list.append(tel)

        return True

    def read_layout(self, layout_name, layout_file):
        """
        read a layout from a layout yaml file
        """

        print(layout_name, layout_file)

        return None

    def print_telescope_list(self):
        """
        print list of telescopes in current layout

        Available formats (examples, column names in ecsv file):
        - telescope_name - default telescope names
        - prod3b_mst_N - North layout (with MST-NectarCam)
        """
        for tel in self.telescope_list:
            tel.print_telescope()

        return None

    def print_array_center(self):
        """
        print coordinates of array center used
        for coordinate transformations
        """
        print('Array center coordinates:')
        if not math.isnan(self.center_lon.value) and \
                not math.isnan(self.center_lat.value):
            print("\t Longitude {0:0.2f}".format(self.center_lon))
            print("\t Latitude {0:0.2f}".format(self.center_lat))
        if not math.isnan(self.center_northing.value) and \
                not math.isnan(self.center_easting.value):
            print("\t Northing {0:0.2f}".format(self.center_northing))
            print("\t Easting {0:0.2f}".format(self.center_easting))
        print("\t Altitude {0:0.2f}".format(self.center_altitude))
        print("\t EGSP %s" % (self.epsg))

    def convert(self):
        """
        conversion depends what is given in the orginal
        telescope list

        after conversion, following coordinates should
        be filled:
        - local transverse Mercator projection
        - Mercator (WGS84) projection
        - UTM coordinate system
        """

        # 1: setup reference coordinate systems

        # Mercator WGS84
        wgs84 = pyproj.CRS("EPSG:4326")
        # local transverse Mercator projection
        crs_local = None
        if self.center_lon is not None \
                and self.center_lat is not None:
            proj4_string = "+proj=tmerc +ellps=WGS84 +datum=WGS84"
            proj4_string = "%s +lon_0=%s +lat_0=%s" % \
                (proj4_string,
                 self.center_lon.value,
                 self.center_lat.value)
            proj4_string = "%s +axis=nwu +units=m +k=1.0" % \
                (proj4_string)
            crs_local = pyproj.CRS.from_proj4(proj4_string)
        # UTM system
        crs_utm = None
        if not math.isnan(self.epsg):
            crs_utm = pyproj.CRS.from_user_input(self.epsg)

        print('Converting telescope coordinates')
        print('\t Local Mercator projection:', crs_local)
        print('\t UTM system: ', crs_utm)

        for tel in self.telescope_list:
            # first possibilities: crs_local given
            if crs_local:
                tel.convert_local_to_mercator(crs_local, wgs84)
                tel.convert_local_to_utm(crs_local, crs_utm)
            # second possibility: crs_utm given
            if crs_utm:
                tel.convert_utm_to_mercator(crs_utm, wgs84)
                tel.convert_utm_to_local(crs_utm, crs_local)
            # convert altitude
            tel.convert_altitude(self.center_altitude)
