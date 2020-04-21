#!/usr/bin/python
"""
print a list of telescopes (optional from a subarray)

python ./print_layout.py  -h for command line options
"""
import argparse
import layout_array


def main():
    """
    telescope positions and layouts
    """

    parser = argparse.ArgumentParser(
        description="print a list of telescopes (optional from a subarray)")
    parser.add_argument("-v", "--verbosity",
                        type=int, choices=[0, 1, 2],
                        help="increase output verbosity",
                        default=0)
    parser.add_argument("telescope_list",
                        help="telescope list")
    parser.add_argument("--layout_list",
                        help="list of layouts")
    parser.add_argument("--layout_name",
                        help="layout to be used",
                        default="baseline")
    args = parser.parse_args()

    layout = layout_array.ArrayData(args.verbosity)
    if layout.read_telescope_list(args.telescope_list):
        layout.convert_coordinates()
        layout.print_array_center()
        layout.read_layout(args.layout_list, args.layout_name)
        layout.print_telescope_list()


if __name__ == "__main__":
    main()
