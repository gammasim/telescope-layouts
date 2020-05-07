#!/usr/bin/python
"""
print a list of telescopes (optional from a subarray)

python ./print_layout.py  -h for command line options
"""
import argparse
import logging
import layout_array

logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.DEBUG)


def main():
    """
    telescope positions and layouts
    """

    parser = argparse.ArgumentParser(
        description='print a list of telescopes (optional from a subarray)')
    parser.add_argument('telescope_list',
                        help='telescope list')
    parser.add_argument('--layout_list',
                        help='list of layouts')
    parser.add_argument('--layout_name',
                        help='layout to be used',
                        default='baseline')
    parser.add_argument('--compact',
                        help='print compact list of telescope positions',
                        type=bool, default=False)
    args = parser.parse_args()

    layout = layout_array.ArrayData()
    if layout.read_telescope_list(args.telescope_list):
        layout.convert_coordinates()
        layout.print_array_center()
        layout.print_corsika_parameters()
        layout.read_layout(args.layout_list, args.layout_name)
        layout.print_telescope_list(args.compact)


if __name__ == '__main__':
    main()
