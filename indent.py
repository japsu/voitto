#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tappio import read_file, write_file
import sys

def main(input_filename=None, output_filename=None):
    document = read_file(input_filename)
    write_file(output_filename, document, pretty_print=True)

if __name__ == "__main__":
    main(*sys.argv[1:])
