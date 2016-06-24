#!/usr/bin/env python

from argparse import ArgumentParser
from struct import unpack_from
from sys import stderr


class Namespace():
    def __str__(self):
        return str(self.__dict__)


def parse_args():
    parser = ArgumentParser(
        description='Convert IT module to and from a plain-text format. This '
                    'format includes only song name, orders, and pattern '
                    'data.')
    parser.add_argument(
        'infile', metavar='INFILE', help='input file (.it or .txt)')
    parser.add_argument(
        'outfile', metavar='OUTFILE', help='output file (.it or .txt)')
    return parser.parse_args()


def die(*args):
    print('fatal:', *args, file=stderr)
    exit(1)


def read_module_pattern(data, offset):
    channels = []
    # TODO
    return channels


def read_module(path):
    with open(path, 'rb') as f:
        data = f.read()

    if unpack_from('4s', data, 0x0)[0].decode() != 'IMPM':
        die('%s is not an IT module' % path)

    mod = Namespace()
    mod.songname = \
        unpack_from('26s', data, 0x4)[0].decode().strip('\0')
    ordnum, insnum, smpnum, patnum = unpack_from('4H', data, 0x20)
    mod.orders = unpack_from('%dB' % ordnum, data, 0xc0)[:-1]

    pattern_offsets = \
        unpack_from('=%dL' % patnum, data, 0xc0 + ordnum + insnum*4 + smpnum*4)
    mod.patterns = []
    for offset in pattern_offsets:
        pattern = read_module_pattern(data, offset)
        mod.patterns.append(pattern)

    return mod


def write_module(mod, path):
    # TODO
    print(mod)


def read_text(path):
    mod = Namespace()
    # TODO
    return mod


def write_text(mod, path):
    # TODO
    print(mod)


def main():
    args = parse_args()

    if args.infile.lower().endswith('.it'):
        mod = read_module(args.infile)
        write_text(mod, args.outfile)
    elif args.outfile.lower().endswith('.txt'):
        mod = read_text(args.infile)
        write_module(mod, args.outfile)
    else:
        die('input file must have extension .it or .txt')


if __name__ == '__main__':
    main()
