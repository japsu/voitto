#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab


from tappio import loadf, dumpf


def sort_events(events):
    events.sort(key=lambda x: (x.date, x.number))


def sort_accounts(accounts):
    assets, liabilities, result = accounts
    recursively_sort_subaccounts(assets)
    recursively_sort_subaccounts(liabilities)
    recursively_sort_subaccounts(result)


def recursively_sort_subaccounts(account):
    account.subaccounts.sort(key=lambda x: x.number)

    for subaccount in account.subaccounts:
        recursively_sort_subaccounts(subaccount)


def renumber_events(events, start=1):
    for num, event in enumerate(events, start=start):
        event.number = num


def renumber(input_filename=None, output_filename=None):
    document = loadf(input_filename)
    sort_accounts(document.accounts)
    sort_events(document.events)
    renumber_events(document.events)
    dumpf(output_filename, document)


def main():
    from sys import argv
    renumber(*argv[1:])


if __name__ == "__main__":
    main()
