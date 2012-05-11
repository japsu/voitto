#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab


from tappio import loadf
from csv import writer
from collections import defaultdict


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


def main():
    from sys import argv
    input_filename = argv[1] if len(argv) >= 2 else None

    document = loadf(input_filename)
    earnings = collect_earnings(document.events)
    print_earnings(document.accounts[2], earnings)

if __name__ == "__main__":
    main()
