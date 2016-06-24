#!/usr/bin/env python

from argparse import ArgumentParser
from base64 import b64encode, b64decode
from struct import unpack_from
from sys import stderr


class Namespace():
    def __str__(self):
        return str(self.__dict__)


def parse_args():
    parser = ArgumentParser(
        description='Convert IT module to and from a Base64 plain-text '
                    'format. This format does not include PCM sample data. '
                    'When converting from text to module, the samples are '
                    'loaded based on filename from the current directory, or '
                    'an alternate directory supplied by the -d option.')
    parser.add_argument(
        'infile', metavar='INFILE', help='input file (.it or .txt)')
    parser.add_argument(
        'outfile', metavar='OUTFILE', help='output file (.it or .txt)')
    parser.add_argument(
        '-d', '--dir', default='.', help='directory containing samples')
    return parser.parse_args()


def die(*args):
    print('fatal:', *args, file=stderr)
    exit(1)


def module_to_text(inpath, outpath):
    with open(inpath, 'rb') as f:
        data = f.read()

    if unpack_from('4s', data, 0x0)[0].decode() != 'IMPM':
        die('%s is not an IT module' % path)

    ordnum, insnum, smpnum, patnum = unpack_from('4H', data, 0x20)
    ins_offsets = unpack_from('=%dL' % insnum, data, 0xc0 + ordnum)
    smp_offsets = unpack_from('=%dL' % patnum, data, 0xc0 + ordnum + insnum*4)
    pat_offsets = \
        unpack_from('=%dL' % patnum, data, 0xc0 + ordnum + insnum*4 + smpnum*4)

    with open(outpath, 'w') as f:
        f.write('[Header]\n')
        f.write(b64encode(data[:0xc0]).decode() + '\n')
        f.write('[Orders]\n')
        f.write(b64encode(data[0xc0:0xc0+ordnum]).decode() + '\n')
        f.write('[Instruments]\n')
        for offset in ins_offsets:
            f.write(b64encode(data[offset:offset+554]).decode() + '\n')
        f.write('[Samples]\n')
        for offset in smp_offsets:
            f.write(b64encode(data[offset:offset+0x40]).decode() + '\n')
        f.write('[Patterns]\n')
        for offset in pat_offsets:
            length = unpack_from('=H', data, offset)[0]
            f.write(b64encode(data[offset:offset+8+length]).decode() + '\n')


def text_to_module(infile, outfile):
    # TODO
    pass


def main():
    args = parse_args()

    if args.infile.lower().endswith('.it'):
        module_to_text(args.infile, args.outfile)
    elif args.outfile.lower().endswith('.txt'):
        text_to_module(args.infile, args.outfile)
    else:
        die('input file must have extension .it or .txt')


if __name__ == '__main__':
    main()
