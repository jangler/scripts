#!/usr/bin/env python

from argparse import ArgumentParser
from base64 import b64decode, b64encode
from os.path import join
from struct import pack, unpack_from
from sys import stderr

FLAG_SAMPLE_ASSOCIATED = 1<<0
FLAG_16BIT = 1<<1


def parse_args():
    parser = ArgumentParser(
        description='Convert IT module to and from a Base64 plain-text '
                    'format. This format does not include PCM sample data. '
                    'Sample data is dumped to and loaded from files in the '
                    'working directory, or an alternate directory supplied '
                    'by the -d option.')
    parser.add_argument(
        'infile', metavar='INFILE', help='input file (.it or .txt)')
    parser.add_argument(
        'outfile', metavar='OUTFILE', help='output file (.it or .txt)')
    parser.add_argument(
        '-d', '--dir', default='', help='directory containing samples')
    return parser.parse_args()


def die(*args):
    print('fatal:', *args, file=stderr)
    exit(1)


def dump_sample(data, offset, smpdir, smp_num):
    smp_name = unpack_from('26s', data, offset+0x14)[0].decode().strip('\0 ')
    smp_flags = unpack_from('B', data, offset+0x12)[0]
    if smp_name:
        smp_length = unpack_from('=I', data, offset+0x30)[0]
        if smp_flags & FLAG_16BIT:
            smp_length *= 2
        smp_point = unpack_from('=I', data, offset+0x48)[0]
        with open(join(smpdir, smp_name + '.raw'), 'wb') as raw:
            raw.write(data[smp_point:smp_point+smp_length])
    elif smp_flags & FLAG_SAMPLE_ASSOCIATED:
        print('could not export nameless sample %02d' % smp_num, file=stderr)


def module_to_text(inpath, outpath, smpdir):
    with open(inpath, 'rb') as f:
        data = f.read()

    if unpack_from('4s', data, 0x0)[0].decode() != 'IMPM':
        die('%s is not an IT module' % path)

    ordnum, insnum, smpnum, patnum = unpack_from('4H', data, 0x20)
    ins_offsets = unpack_from('=%dI' % insnum, data, 0xc0 + ordnum)
    smp_offsets = unpack_from('=%dI' % smpnum, data, 0xc0 + ordnum + insnum*4)
    pat_offsets = \
        unpack_from('=%dI' % patnum, data, 0xc0 + ordnum + insnum*4 + smpnum*4)

    with open(outpath, 'w') as f:
        f.write('[Header]\n')
        f.write(b64encode(data[:0xc0]).decode() + '\n')
        f.write('[Orders]\n')
        f.write(b64encode(data[0xc0:0xc0+ordnum]).decode() + '\n')
        for i, offset in enumerate(ins_offsets):
            f.write('[Instrument%02d]\n' % (i+1))
            f.write(b64encode(data[offset:offset+554]).decode() + '\n')
        for i, offset in enumerate(smp_offsets):
            f.write('[Sample%02d]\n' % (i+1))
            dump_sample(data, offset, smpdir, i+1)
            f.write(b64encode(data[offset:offset+0x50]).decode() + '\n')
        for i, offset in enumerate(pat_offsets):
            f.write('[Pattern%03d]\n' % i)
            length = unpack_from('=H', data, offset)[0]
            f.write(b64encode(data[offset:offset+8+length]).decode() + '\n')


def text_to_module(inpath, outpath, smpdir):
    with open(inpath, 'r') as f:
        lines = [line.strip('\n') for line in f.readlines()]

    if not lines or lines[0] != '[Header]':
        die('%s is not a compatible text file' % inpath)

    header_data = b64decode(lines[1])
    ordnum, insnum, smpnum, patnum = unpack_from('4H', header_data, 0x20)
    ins_offsets = [0xc0 + ordnum + 554*i for i in range(insnum)]
    smp_offsets = [0xc0 + ordnum + 554*insnum + 0x50*i for i in range(smpnum)]
    cur_offset = 0xc0 + ordnum + 554*insnum + 0x50*smpnum
    pat_offsets = []
    i = 0
    while i < len(lines):
        if lines[i].startswith('[Pattern'):
            pat_offsets.append(cur_offset)
            length = unpack_from('H', b64decode(lines[i+1]), 0)[0]
            cur_offset += 8 + length
        i += 1
    offsets = ins_offsets + smp_offsets + pat_offsets
    i = 0
    while i < len(offsets):
        offsets[i] += len(offsets) * 4
        i += 1
    cur_offset += len(offsets) * 4

    samples = []
    wrote_offsets = wrote_orders = is_sample = False
    pos = 0
    with open(outpath, 'wb') as f:
        sections = 'Header', 'Orders', 'Instrument', 'Sample', 'Pattern'
        for line in lines:
            if any(line.startswith('[' + s) for s in sections):
                is_sample = line.startswith('[Sample')
                if line == '[Orders]':
                    wrote_orders = True
                elif wrote_orders and not wrote_offsets:
                    pos += f.write(pack('%dI' % len(offsets), *offsets))
                    wrote_offsets = True
            else:
                data = b64decode(line)
                if is_sample:
                    smp_name = unpack_from(
                        '26s', data, 0x14)[0].decode().strip('\0 ')
                    smp_flags = unpack_from('B', data, 0x12)[0]
                    if smp_name:
                        raw_name = join(smpdir, smp_name + '.raw')
                        with open(raw_name, 'rb') as raw:
                            smp_data = raw.read()
                        smp_point = pack('I', cur_offset)
                        data = data[:0x48] + smp_point + data[0x4c:]
                        cur_offset += len(smp_data)
                        samples.append(smp_data)
                    elif smp_flags & FLAG_SAMPLE_ASSOCIATED:
                        print('could not import nameless sample %02d' % (i+1),
                              file=stderr)
                pos += f.write(data)
        for sample in samples:
            pos += f.write(sample)


def main():
    args = parse_args()

    if args.infile.lower().endswith('.it'):
        module_to_text(args.infile, args.outfile, args.dir)
    elif args.infile.lower().endswith('.txt'):
        text_to_module(args.infile, args.outfile, args.dir)
    else:
        die('input file must have extension .it or .txt')


if __name__ == '__main__':
    main()
