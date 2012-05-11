#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab


from tappio import loadf, dumpf, Event, Entry
from print_earnings import collect_earnings

from datetime import date, datetime


BALANCES_DEFAULT_DESCRIPTION = "Tilinavaukset"
BALANCES_DEFAULT_NUMBER = 0
DATE_FORMAT = "%Y-%m-%d"


def get_balance_accounts(accounts):
    stack = list()
    # (vastaavaa, vastattavaa, tulos)
    stack.extend(accounts[:2])
    result = set()

    while stack:
        cur = stack.pop()
        if cur.number is not None:
            result.add(cur.number)

        for subaccount in cur.subaccounts:
            stack.append(subaccount)

    return result


def balances(document, at_date=None, description=BALANCES_DEFAULT_DESCRIPTION,
        number=BALANCES_DEFAULT_NUMBER):
    if at_date is None:
        at_date = date.today()

    result = Event(date=at_date, description=description, number=number)
    balances = collect_earnings([i for i in document.events if i.date < at_date])
    balance_accounts = get_balance_accounts(document.accounts)

    for account_number, cents in balances.iteritems():
        if account_number in balance_accounts:
            result.entries.append(Entry(account_number=account_number, cents=cents))

    return result


def drop_extra_events(document, from_date, to_date):
    relevant_events = [i for i in document.events if i.date >= from_date
        and i.date <= to_date]

    document.events = relevant_events


def inject_balances(document, at_date):
    balances_event = balances(document, at_date)
    document.events.insert(0, balances_event)


def extract(from_date_str, to_date_str, input_filename=None, output_filename=None):
    from_date = datetime.strptime(from_date_str, DATE_FORMAT).date()
    to_date = datetime.strptime(to_date_str, DATE_FORMAT).date()

    if from_date > to_date:
        raise ValueError("from_date > to_date")

    document = loadf(input_filename)

    inject_balances(document, from_date)
    drop_extra_events(document, from_date, to_date)

    document.begin = from_date
    document.end = to_date

    dumpf(output_filename, document)


def main():
    from sys import argv
    extract(*argv[1:])


if __name__ == "__main__":
    main()    
