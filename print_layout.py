#!/usr/bin/python
"""
print a list of telescopes or array layout
"""
import getopt
import sys
import layout_array


def print_help():
    """
    print help messages
    """
    print("python ./print_layout.py \n \
            --telescope_list=<telescope list> \n \
            --layout_list=<list of layouts> \n \
            --layout=<layout name> \n \
            --UTM (convert to UTM)")
    print("")
    print("print a list of telescopes (optional from a subarray)")
    print("")
    sys.exit(2)


def main(argv):
    """
    telescope positions and layouts
    """

    telescope_list = None
    array_list = None
    array_layout = "baseline"
    verbose = False

    try:
        opts, args = getopt.getopt(argv, "h",
                                   ["telescope_list=",
                                    "layout_list=",
                                    "layout=",
                                    "help"])
    except getopt.GetoptError:
        print_help()

    if len(opts) == 0:
        print_help()

    for opt, arg in opts:
        if opt == ('-h', '--help'):
            print_help()
            sys.exit()
        elif opt in "--telescope_list":
            telescope_list = arg
        elif opt in "--layout_list":
            layout_list = arg
        elif opt in "--layout":
            layout = arg
        elif opt in "--verbose":
            verbose = True
        else:
            print_help()

    layout = layout_array.ArrayData(verbose)
    if layout.read_telescope_list(telescope_list):
        layout.convert()
        layout.print_array_center()
        layout.print_telescope_list()


if __name__ == "__main__":
    main(sys.argv[1:])
