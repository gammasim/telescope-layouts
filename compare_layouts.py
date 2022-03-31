#!/usr/bin/python
"""
compare telescope positions from two lists of telescopes

python ./compare_layouts.py -h for command line options
"""
import argparse
import logging
import layout_array

logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.DEBUG)


def main():
    """
    compare telescope positions
    """

    parser = argparse.ArgumentParser(
        description="compare telescope positions from two lists of telescopes"
    )
    parser.add_argument("telescope_list_1", help="telescope list #1")
    parser.add_argument("telescope_list_2", help="telescope list #2")
    parser.add_argument(
        "--tolerance_geod",
        help="minimum difference between telescope positions for printing",
        type=float,
        default=0.0,
    )
    parser.add_argument(
        "--tolerance_alt",
        help="minimum difference between telescope altitude for printing",
        type=float,
        default=0.0,
    )
    args = parser.parse_args()

    layout_1 = layout_array.ArrayData()
    layout_2 = layout_array.ArrayData()
    if layout_1.read_telescope_list(
        args.telescope_list_1
    ) and layout_2.read_telescope_list(args.telescope_list_2):
        layout_1.convert_coordinates()
        layout_2.convert_coordinates()

        layout_1.compare_array_center(layout_2)
        layout_1.compare_telescope_positions(
            layout_2, args.tolerance_geod, args.tolerance_alt
        )


if __name__ == "__main__":
    main()
