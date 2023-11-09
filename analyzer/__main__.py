import sys
from argparse import ArgumentParser
from analyzer import Analyzer


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--log", type=str, default="log.txt", help="")
    parsed_args = parser.parse_args(sys.argv[1:])

    analyzer = Analyzer()
    analyzer.run(parsed_args.log)
