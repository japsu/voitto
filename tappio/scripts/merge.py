#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab


from tappio import Document, loadf, dumpf


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
    return d


def merge(*documents):
    return reduce(merge_two, documents)


def merge_files(output_filename, *input_filenames):
    documents = (loadf(filename) for filename in input_filenames)
    merged = merge(*documents)
    dumpf(output_filename, merged)


def main():
    from sys import argv
    merge_files(*argv[1:])


if __name__ == "__main__":
    main()
