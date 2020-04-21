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

    def __init__(self, verbose_debug=True):
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
                tel.x = row['pos_x']*table['pos_x'].unit
            if 'pos_y' in table.colnames:
                tel.y = row['pos_y']*table['pos_y'].unit
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

    def read_layout(self, layout_list, layout_name):
        """
        read a layout from a layout yaml file
        """

        print(layout_name, layout_list)

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

    def convert_coordinates(self):
        """
        conversion depends what is given in the orginal
        telescope list

        after conversion, following coordinates should
        be filled:
        - local transverse Mercator projection
        - Mercator (WGS84) projection
        - UTM coordinate system
        """

        print('Converting telescope coordinates')

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
            print('\t Local Mercator projection:', crs_local)
        # UTM system
        crs_utm = None
        if not math.isnan(self.epsg):
            crs_utm = pyproj.CRS.from_user_input(self.epsg)
            print('\t UTM system: ', crs_utm)

        # 2. convert coordinates
        for tel in self.telescope_list:
            tel.convert(crs_local, wgs84, crs_utm, self.center_altitude)

    def compare_array_center(self, layout2):
        """
        compare array center coordinates of this array
        with another one
        """
        print('comparing array center coordinates')
        print('')
        print("{0:12s} | {1:>16s} | {2:>16s} | {3:>16s} | ".format(
            "", "layout_1", "layout_2", "difference"))
        print("{0:12s} | {1:>16s} | {2:>16s} | {3:>16s} | ".format(
            "-----", "-----", "-----", "-----"))
        print("{0:12s} | {1:12.2f} | {2:12.2f} | {3:12.2f} |".format(
            "Longitude",
            self.center_lon, layout2.center_lon,
            self.center_lon-layout2.center_lon))
        print("{0:12s} | {1:12.2f} | {2:12.2f} | {3:12.2f} |".format(
            "Latitude",
            self.center_lat, layout2.center_lat,
            self.center_lat-layout2.center_lat))
        print("{0:12s} | {1:14.2f} | {2:14.2f} | {3:14.2f} |".format(
            "Northing",
            self.center_northing, layout2.center_northing,
            self.center_northing-layout2.center_northing))
        print("{0:12s} | {1:14.2f} | {2:14.2f} | {3:14.2f} |".format(
            "Easting",
            self.center_easting, layout2.center_easting,
            self.center_easting-layout2.center_easting))
        print("{0:12s} | {1:14.2f} | {2:14.2f} | {3:14.2f} |".format(
            "Altitude",
            self.center_altitude, layout2.center_altitude,
            self.center_altitude-layout2.center_altitude))

    def compare_telescope_positions(self, layout2, compare_coordinate, tolerance=0.):
        """
        compare telescope positions of two telescope lists
        """
        print('')
        print('comparing telescope positions')
        print("{0:s} coordinate system (tolerance {1:f})".format(
            compare_coordinate, tolerance))
        print('')
        # Step 1: make sure that lists are compatible
        for tel_1 in self.telescope_list:
            telescope_found = False
            for tel_2 in layout2.telescope_list:
                if tel_1.name == tel_2.name:
                    telescope_found = True

            if not telescope_found:
                print("Telescope {0:s} from list 1 not found in list 2".format(
                    tel_1.name))

        # Step 2: compare coordinate values
        if compare_coordinate.lower() == "local":
            self.compare_telescope_positions_local(layout2, tolerance)
        elif compare_coordinate.lower() == "utm":
            self.compare_telescope_positions_utm(layout2, tolerance)
        elif compare_coordinate.lower() == "mercator":
            self.compare_telescope_positions_mercator(layout2, tolerance)
        elif compare_coordinate.lower() == "altitude":
            self.compare_telescope_altitude(layout2, tolerance)
        else:
            print("Error: unknown coordinate system ({0:s})".format(
                compare_coordinate))

    def compare_telescope_positions_local(self, layout2, tolerance=0.):
        """
        compare telescope positions in local coordinates
        """

        print("{0:12s} | {1:>16s} | {2:>16s} | {3:>16s} | {4:>16s} | {5:>16s} | {6:>16s} |".format(
            "telescope", "x(layout_1)", "x(layout_2)", "delta x",
            "y(layout_1)", "y(layout_2)", "delta y"))
        print("{0:12s} | {1:>16s} | {2:>16s} | {3:>16s} | {4:>16s} | {5:>16s} | {6:>16s} |".format(
            "-----", "-----", "-----", "-----",
            "-----", "-----", "-----"))
        for tel_1 in self.telescope_list:
            for tel_2 in layout2.telescope_list:
                if tel_1.name == tel_2.name:
                    diff = math.sqrt((tel_1.x.value-tel_2.x.value)**2
                                     + (tel_1.y.value-tel_2.y.value)**2)
                    if diff > tolerance:
                        print("{0:12s} | {1:14.2f} | {2:14.2f} | {3:14.2f} | {4:14.2f} | {5:14.2f} | {6:14.2f} |".format(
                            tel_1.name,
                            tel_1.x, tel_2.x,
                            tel_1.x-tel_2.x,
                            tel_1.y, tel_2.y,
                            tel_1.y-tel_2.y))

    def compare_telescope_positions_utm(self, layout2, tolerance=0.):
        """
        compare telescope positions in utm coordinates
        """

        print("E=Easting, N=Northing")
        print("")
        print("{0:12s} | {1:>16s} | {2:>16s} | {3:>16s} | {4:>16s} | {5:>16s} | {6:>16s} |".format(
            "telescope", "E(layout_1)", "E(layout_2)", "delta E",
            "N(layout_1)", "N(layout_2)", "delta N"))
        print("{0:12s} | {1:>16s} | {2:>16s} | {3:>16s} | {4:>16s} | {5:>16s} | {6:>16s} |".format(
            "-----", "-----", "-----", "-----",
            "-----", "-----", "-----"))
        for tel_1 in self.telescope_list:
            for tel_2 in layout2.telescope_list:
                if tel_1.name == tel_2.name:
                    diff = math.sqrt((tel_1.utm_east.value-tel_2.utm_east.value)**2
                                     + (tel_1.utm_north.value-tel_2.utm_north.value)**2)
                    if diff > tolerance:
                        print("{0:12s} | {1:14.2f} | {2:14.2f} | {3:14.2f} | {4:14.2f} | {5:14.2f} | {6:14.2f} |".format(
                            tel_1.name,
                            tel_1.utm_east, tel_2.utm_east,
                            tel_1.utm_east-tel_2.utm_east,
                            tel_1.utm_north, tel_2.utm_north,
                            tel_1.utm_north-tel_2.utm_north))

    def compare_telescope_positions_mercator(self, layout2, tolerance=0.):
        """
        compare telescope positions in mercator coordinates
        """

        print("")
        print("{0:12s} | {1:>18s} | {2:>18s} | {3:>18s} | {4:>18s} | {5:>18s} | {6:>18s} |".format(
            "telescope", "lon(layout_1)", "lon(layout_2)", "delta lon",
            "lat(layout_1)", "lat(layout_2)", "delta lat"))
        print("{0:12s} | {1:>18s} | {2:>18s} | {3:>18s} | {4:>18s} | {5:>18s} | {6:>18s} |".format(
            "-----", "-----", "-----", "-----",
            "-----", "-----", "-----"))
        for tel_1 in self.telescope_list:
            for tel_2 in layout2.telescope_list:
                if tel_1.name == tel_2.name:
                    diff = math.sqrt((tel_1.lon.value-tel_2.lon.value)**2
                                     + (tel_1.lat.value-tel_2.lat.value)**2)
                    if diff > tolerance:
                        print("{0:12s} | {1:14.5f} | {2:14.5f} | {3:14.5f} | {4:14.5f} | {5:14.5f} | {6:14.5f} |".format(
                            tel_1.name,
                            tel_1.lon, tel_2.lon,
                            tel_1.lon-tel_2.lon,
                            tel_1.lat, tel_2.lat,
                            tel_1.lat-tel_2.lat))

    def compare_telescope_altitude(self, layout2, tolerance=0.):
        """
        compare telescope altitude
        """

        print("")
        print("{0:12s} | {1:>16s} | {2:>16s} | {3:>16s} | {4:>16s} | {5:>16s} | {6:>16s} |".format(
            "telescope", "z(layout_1)", "z(layout_2)", "delta z",
            "alt(layout_1)", "alt(layout_2)", "delta alt"))
        print("{0:12s} | {1:>16s} | {2:>16s} | {3:>16s} | {4:>16s} | {5:>16s} | {6:>16s} |".format(
            "-----", "-----", "-----", "-----",
            "-----", "-----", "-----"))
        for tel_1 in self.telescope_list:
            for tel_2 in layout2.telescope_list:
                if tel_1.name == tel_2.name:
                    diff = abs(tel_1.alt.value-tel_2.alt.value)
                    if diff > tolerance:
                        print("{0:12s} | {1:14.5f} | {2:14.5f} | {3:14.5f} | {4:14.5f} | {5:14.5f} | {6:14.5f} |".format(
                            tel_1.name,
                            tel_1.z, tel_2.z,
                            tel_1.z-tel_2.z,
                            tel_1.alt, tel_2.alt,
                            tel_1.alt-tel_2.alt))
