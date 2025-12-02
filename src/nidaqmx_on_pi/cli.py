"""Simple CLI for nidaqmx_on_pi scaffold."""

import argparse
from . import greet


def main() -> None:
    parser = argparse.ArgumentParser(prog="nidaqmx_on_pi")
    parser.add_argument("name", nargs="?", default="world")
    args = parser.parse_args()
    print(greet(args.name))


if __name__ == "__main__":
    main()
