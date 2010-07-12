#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tappio import read_file
import sys

def print_accounts(accounts, indent=0, indent_increment=2):
    for account in accounts:
        if account.number is not None:
            print "%s%d %s" % (" "*indent, account.number, account.name)
        else:
            print "%s%s" % (" "*indent, account.name)
        print_accounts(account.subaccounts, indent=indent+indent_increment)

def main(input_filename=None):
    document = read_file(input_filename)
    print_accounts(document.accounts)

if __name__ == "__main__":
    main(*sys.argv[1:])
