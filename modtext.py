#!/usr/bin/env python

import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description='Convert IT modules to and from a plain-text format.')
    parser.add_argument(
        'infile', metavar='INFILE', help='input file (.it or .txt)')
    parser.add_argument(
        'outfile', metavar='OUTFILE', help='output file (.it or .txt)')
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='enable verbose logging')
    return parser.parse_args()


def read_module(path, verbose):
    module = {}
    return module


def write_module(module, path, verbose):
    pass


def read_text(path, verbose):
    module = {}
    return module


def write_text(module, path, verbose):
    pass


def main():
    args = parse_args()

    if args.infile.lower().endswith('.it'):
        module = read_module(args.infile, args.verbose)
        write_text(module, args.outfile, args.verbose)
    elif args.outfile.lower().endswith('.txt'):
        module = read_text(args.infile, args.verbose)
        write_module(module, args.outfile, args.verbose)
    else:
        print('input file must have extension .it or .txt', file=sys.stderr)


if __name__ == '__main__':
    main()
