#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tappio import read_file, write_file
import sys

def move_entries(events, from_account_num, to_account_num):
    for event in events:
        for entry in event.entries:
            if entry.account_number == from_account_num:
                entry.account_number = to_account_num

def main(from_account_num, to_account_num, input_filename=None, output_filename=None):
    from_account_num = int(from_account_num)
    to_account_num = int(to_account_num)
    document = read_file(input_filename)
    move_entries(document.events, from_account_num, to_account_num)
    write_file(output_filename, document)

if __name__ == "__main__":
    main(*sys.argv[1:])
