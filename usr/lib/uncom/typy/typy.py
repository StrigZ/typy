#!/usr/bin/python3

import argparse
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from application import Application


def parse_args():
    parser = argparse.ArgumentParser(
        description="Uncom App Template demonstration application. Can be used via terminal and GUI.",
        epilog="Start without parameters to view help.",
    )
    parser.add_argument(
        "-g", "--gui", action="store_true", help="run with graphical UI"
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-a", "--option-a", action="store_true", help="some option A")
    group.add_argument("-b", "--option-b", action="store_true", help="some option B")
    return parser.parse_args()


def main():
    sys.argv = [sys.argv[0]]
    app = Application()
    sys.exit(app.run(sys.argv))


if __name__ == "__main__":
    main()
