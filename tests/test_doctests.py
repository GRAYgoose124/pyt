import unittest
import doctest
import pyt.utils
import pyt.deltafile


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(pyt.utils))
    tests.addTests(doctest.DocTestSuite(pyt.deltafile))
    return tests
