#
#
import sys
import math
from astropy.table import Table
from astropy import units as u
import pyproj

class telescopeData:
    """
    data class for telescope IDs and
    positions
    """

    def __init__(self):
        self.name=None
        self.x=math.nan*u.meter
        self.y=math.nan*u.meter
        self.z=math.nan*u.meter
        self.lon=math.nan*u.deg
        self.lat=math.nan*u.deg
        self.utm_east=math.nan*u.meter
        self.utm_north=math.nan*u.meter
        self.alt=math.nan*u.meter
        self.prod_id={}

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
            print("\t",self.prod_id)

class layoutData:
    """
    layout class for
    - storage of telescope position
    - conversion of coordinate systems of positions
    """

    def __init__(self):
        self.name=None
        self.telescope_list=[]
        # centre of the array
        self.EPSG=math.nan
        self.center_northing=math.nan*u.meter
        self.center_easting=math.nan*u.meter
        self.center_lon=None
        self.center_lat=None
        self.center_altitude=math.nan*u.meter

        self.verbose=True

    def read_telescope_list(self, telescope_file):
        """
        read list of telescopes from a ecsv file
        """
        try:
            t=Table.read(telescope_file,  format='ascii.ecsv')
        except Exception as ex:
            print('Error reading telescopes from ', telescope_file)
            print(ex.args)
            return False
        if self.verbose:
            print(t.meta)
            print(t)
        print("reading telescope list from ", telescope_file)
        # require telescope_name in telescope lists
        if 'telescope_name' not in t.colnames:
            print('Error reading telescope list from ', telescope_file)
            print('   required column telescope_name missing')
            print(t.meta)
            return False
        # reference coordinate system
        if 'EPSG' in t.meta:
            self.EPSG=t.meta['EPSG']
        if 'center_northing' in t.meta and \
                'center_easting' in t.meta:
                self.center_northing=u.Quantity(t.meta['center_northing'])
                self.center_easting=u.Quantity(t.meta['center_easting'])
        if 'center_lon' in t.meta and \
                'center_lat' in t.meta:
                    self.center_lon=u.Quantity(t.meta['center_lon'])
                    self.center_lat=u.Quantity(t.meta['center_lat'])
        if 'center_alt' in t.meta:
            self.center_altitude=u.Quantity(t.meta['center_alt'])
        # initialise telescope lists from productions
        prod_list=[]
        for row_name in t.colnames:
            if row_name.find("prod")>=0:
                prod_list.append(row_name)

        for row in t:
            tel = telescopeData()
            tel.name=row['telescope_name']
            if 'pos_x' in t.colnames:
                # TMPTMP
                tel.y=-1.*row['pos_x']*t['pos_x'].unit
            if 'pos_y' in t.colnames:
                # TMPTMP
                tel.x=row['pos_y']*t['pos_y'].unit
            if 'pos_z' in t.colnames:
                tel.z=row['pos_z']*t['pos_z'].unit
            if 'utm_east' in t.colnames:
                tel.utm_east=row['utm_east']*t['utm_east'].unit
            if 'utm_north' in t.colnames:
                tel.utm_north=row['utm_north']*t['utm_north'].unit
            if 'alt' in t.colnames:
                tel.alt=row['alt']*t['alt'].unit
            if 'lon' in t.colnames:
                tel.lon=row['lon']*t['lon'].unit
            if 'lat' in t.colnames:
                tel.utm_north=row['lat']*t['lat'].unit

            for p in prod_list:
                tel.prod_id[p]=row[p]

            self.telescope_list.append(tel)

        return True

    def read_layout(self, layout_name, layout_file):
        """
        read a layout from a layout yaml file
        """

        return None

    def print_telescope_list(self):
        """
        print list of telescopes in current layout
        
        Available formats (examples, column names in ecsv file):
        - telescope_name - default telescope names
        - prod3b_mst_N - North layout (with MST-NectarCam)
        """
        for e in self.telescope_list:
            e.print_telescope()

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
        print("\t EGSP %s" % (self.EPSG))

    def convert(self):
        """
        conversion depends what is given in the orginal
        telescope list

        after conversion, following coordinates should
        be filled:
        - local transverse Mercator projection
        - Mercador (WGS84) projection
        - UTM coordinate system
        """

        # 1: setup reference coordinate systems

        # Mercator WGS84
        wgs84=pyproj.CRS("EPSG:4326")
        # local transverse Mercator projection
        crs_local=None
        if self.center_lon is not None \
                and self.center_lat is not None:
                proj4_string="+proj=tmerc +ellps=WGS84 +datum=WGS84"
                proj4_string="%s +lon_0=%s +lat_0=%s" % \
                        (proj4_string, \
                        self.center_lon.value, \
                        self.center_lat.value)
                proj4_string="%s +axis=nwu +units=m +k=1.0" % \
                        (proj4_string)
                crs_local = pyproj.CRS.from_proj4(proj4_string)
        # UTM system
        crs_utm=None
        if not math.isnan(self.EPSG):
            crs_utm = pyproj.CRS.from_user_input(self.EPSG)

        print('Converting telescope coordinates')

        # first possibilities: crs_local given
        if crs_local:
            print('Local Mercator projection:', crs_local)
            for t in self.telescope_list:
                if not math.isnan(t.x.value) \
                        and not math.isnan(t.y.value):
                    # calculate lon/lat
                    if math.isnan(t.lon.value) \
                            or math.isnan(t.lat.value):
                        t.lon,t.lat = \
                                pyproj.transform(crs_local,wgs84,
                                        t.x.value,t.y.value) \
                                                *u.deg
                    # calculate utm coordinates
                    if crs_utm and \
                            (math.isnan(t.utm_east.value) \
                            or math.isnan(t.utm_north.value)):
                            t.utm_east, t.utm_north = \
                                    pyproj.transform(crs_local,crs_utm,
                                            t.x.value,t.y.value) \
                                                    *u.meter
        # second possibility: crs_utm given
        if crs_utm:
            print('UTM system: ',crs_utm)
            for t in self.telescope_list:
                if not math.isnan(t.utm_east.value) \
                        and not math.isnan(t.utm_north.value):
                    # calculate lon/lat
                    if math.isnan(t.lon.value) \
                            or math.isnan(t.lat.value):
                        t.lon,t.lat = \
                                pyproj.transform(crs_utm,wgs84,
                                        t.utm_east.value,t.utm_north.value) \
                                                *u.deg
                    if math.isnan(t.x.value) or math.isnan(t.y.value):
                        t.x,t.y = \
                                pyproj.transform(crs_utm,crs_local,
                                        t.utm_east.value,t.utm_north.value) \
                                                *u.meter

        # altitude
        if not math.isnan(self.center_altitude.value):
            for t in self.telescope_list:
                if math.isnan(t.z.value) and \
                        not math.isnan(t.alt.value):
                    t.z=t.alt-self.center_altitude
                if math.isnan(t.alt.value) and \
                        not math.isnan(t.z.value):
                    t.alt=t.z+self.center_altitude


def main(argv):
    """
    telescope positions and layouts
    """

    telescope_file="SB.ecsv"
    telescope_file="telescope_positions_south.ecsv"
    array_file="layouts_south.yaml"
    array_layout="baseline"

    layout = layoutData()
    if layout.read_telescope_list(telescope_file):
        layout.convert()
        layout.print_array_center()
        layout.print_telescope_list()


if __name__ == "__main__":
    main(sys.argv[1:])
