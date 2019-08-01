#!/usr/bin/env python

import sys

from csv import writer
from collections import defaultdict

from tappio import loadf

def format_money(cents):
    cents = -cents
    return "%d.%02d" % divmod(cents, 100)


def print_earnings(earnings_account, earnings, stream=sys.stdout):
    w = writer(stream)
    recursively_print_earnings(earnings_account, earnings, w)


def recursively_print_earnings(account, earnings, w):
    if account.number is not None:
        w.writerow([account.number, account.name, format_money(earnings[account.number])])

    for subaccount in account.subaccounts:
        recursively_print_earnings(subaccount, earnings, w)


def collect_earnings(events):
    earnings = defaultdict(int)

    for event in events:
        for entry in event.entries:
            earnings[entry.account_number] += entry.cents

    return earnings


def print_earnings_util(input_filename=None, output_filename=None):
    input_filename = argv[1] if len(argv) >= 2 else None

    document = loadf(input_filename)
    earnings = collect_earnings(document.events)

    with output_stream(output_filename) as out:
        print_earnings(document.accounts[2], earnings, out)

def main():
    print_earnings_util(*sys.argv[1:])

if __name__ == "__main__":
    main()
