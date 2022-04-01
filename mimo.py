import argparse

from mimo.fuzzer import Fuzzer
from mimo.config import Configuration


def main(args):
    config = Configuration(args.config_file)

    fuzzer = Fuzzer(config, args.seed)

    fuzzer.initialize()
    fuzzer.run()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', help='Configuration file (json)')
    parser.add_argument('--seed', help='Set the random seed')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args)

