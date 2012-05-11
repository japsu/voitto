#!/usr/bin/env python
# vim: shiftwidth=4 expandtab
# encoding: utf-8

from test_tappio import run_tests
from tracer import traceit
from sys import settrace

settrace(traceit)
run_tests()
