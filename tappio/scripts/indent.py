#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tappio import loadf, dumpf

def indent(input_filename=None, output_filename=None):
    document = loadf(input_filename)
    dumpf(output_filename, document, pretty_print=True)


def main():
    from sys import argv
    indent(*argv[1:])


if __name__ == "__main__":
    main()
