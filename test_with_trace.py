from test_tappio import run_tests
from tracer import traceit
from sys import settrace

settrace(traceit)
run_tests()
