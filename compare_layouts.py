#!/usr/bin/python
"""
compare telescope positions from two lists of telescopes

python ./compare_layouts.py -h for command line options
"""
import argparse
import layout_array


def main():
    """
    compare telescope positions
    """

    parser = argparse.ArgumentParser(
        description="compare telescope positions from two lists of telescopes")
    parser.add_argument("-v", "--verbosity",
                        type=int, choices=[0, 1, 2],
                        help="increase output verbosity",
                        default=0)
    parser.add_argument("telescope_list_1",
                        help="telescope list #1")
    parser.add_argument("telescope_list_2",
                        help="telescope list #2")
    parser.add_argument("--coordinatesystem",
                        help="coordinate system",
                        choices=["local", "utm", "mercator", "altitude"],
                        default="local")
    parser.add_argument("--tolerance",
                        help="minimum difference between positions for printing",
                        type=float, default=0.)
    args = parser.parse_args()

    layout_1 = layout_array.ArrayData(args.verbosity)
    layout_2 = layout_array.ArrayData(args.verbosity)
    if layout_1.read_telescope_list(args.telescope_list_1) and \
            layout_2.read_telescope_list(args.telescope_list_2):
        layout_1.convert_coordinates()
        layout_2.convert_coordinates()

        layout_1.compare_array_center(layout_2)
        layout_1.compare_telescope_positions(layout_2,
                                             args.coordinatesystem,
                                             args.tolerance)


if __name__ == "__main__":
    main()
