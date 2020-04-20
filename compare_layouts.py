#!/usr/bin/python
"""
compare telescope positions from two lists of telescopes
"""
import getopt
import sys
import layout_array


def print_help():
    """
    print help messages
    """
    print("python ./compare_layouts.py \n \
            --telescope_list_1=<telescope list #1> \n \
            --telescope_list_2=<telescope list #2> \n \
            --coordinatesystem=<coordinate system> \n \
            --tolerance=<min difference between positions for printing>")
    print("")
    print("compare telescope positions from two telescope list")
    print("\t coordinate systems: local, utm, mercator, altitude")
    print("")
    sys.exit(2)


def main(argv):
    """
    compare telescope positions
    """

    telescope_list_1 = None
    telescope_list_2 = None
    verbose = False
    coordinatesystem = "local"
    tolerance = 0.

    try:
        opts, args = getopt.getopt(argv, "h",
                                   ["telescope_list_1=",
                                    "telescope_list_2=",
                                    "coordinatesystem=",
                                    "tolerance=",
                                    "help"])
    except getopt.GetoptError:
        print_help()

    if len(opts) == 0:
        print_help()

    for opt, arg in opts:
        if opt == ('-h', '--help'):
            print_help()
            sys.exit()
        elif opt in "--telescope_list_1":
            telescope_list_1 = arg
        elif opt in "--telescope_list_2":
            telescope_list_2 = arg
        elif opt in "--verbose":
            verbose = True
        elif opt in "--coordinatesystem":
            coordinatesystem = arg
        elif opt in "--tolerance":
            tolerance = float(arg)
        else:
            print_help()

    layout_1 = layout_array.ArrayData(verbose)
    layout_2 = layout_array.ArrayData(verbose)
    if layout_1.read_telescope_list(telescope_list_1) and \
            layout_2.read_telescope_list(telescope_list_2):
        layout_1.convert()
        layout_2.convert()

        layout_1.compare_array_center(layout_2)
        layout_1.compare_telescope_positions(layout_2,
                                             coordinatesystem,
                                             tolerance)


if __name__ == "__main__":
    main(sys.argv[1:])
