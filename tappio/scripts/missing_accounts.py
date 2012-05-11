#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab


from collections import defaultdict
from tappio import loadf, dumpf


ONLY=True


def flatten_accounts(accounts):
    flat_accounts = dict()

    for branch in accounts:
        _flatten_accounts(branch, flat_accounts)

    return flat_accounts


def _flatten_accounts(account, accounts):
    accounts[account.number] = account

    for subaccount in account.subaccounts:
        _flatten_accounts(subaccount, accounts)


def missing_accounts(*input_filenames):
    input_filenames = set(input_filenames)

    documents = ((filename, loadf(filename)) for filename in input_filenames)
    flat_accounts = dict((filename, flatten_accounts(document.accounts)) for (filename, document) in documents)

    all_accounts = dict()
    map(all_accounts.update, flat_accounts.itervalues())
    
    havity = defaultdict(set)
    for account_num, account in all_accounts.iteritems():
        for filename, accounts in flat_accounts.iteritems():
            if account_num in accounts:
                havity[account_num].add(filename)

    for account_num, filenames in havity.iteritems():
        fmt_filenames = " ".join(filenames)

        if filenames == input_filenames:
            if not ONLY:
                print "{account_num}: ALL  {fmt_filenames}".format(**locals())
        else:
            print "{account_num}: ONLY {fmt_filenames}".format(**locals())
            

def main():
    from sys import argv
    missing_accounts(*argv[1:])


if __name__ == "__main__":
    main()
