#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tappio import Lexer, Parser, Writer
import sys

def combine_accounts(earliers, laters):
    # XXX Seriously fugly hack, do this properly
    return laters

def combine_events(earliers, laters):
    return earliers + laters

def merge_two(earlier, later):
    d = Document()
    d.identity = later.identity if later.identity is not None else earlier.identity
    d.name = later.name if later.name is not None else earlier.identity
    d.begin = min(earlier.begin, later.begin)
    d.end = max(earlier.end, later.end)
    d.accounts = combine_accounts(earlier.accounts, later.accounts)
    d.events = combine_events(earlier.events, later.events)

def merge(*documents):
    return reduce(merge_two, documents)

def main(output_filename, *input_filenames):
    documents = (read_file(filename) for filename in input_filenames)
    merged = merge(*documents)
    write_file(output_filename, merged)

if __name__ == "__main__":
    main(*sys.argv[1:])
