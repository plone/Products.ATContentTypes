"""
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.ftests import atctftestcase

tests = []

class TestATEventFunctional(atctftestcase.ATCTIntegrationTestCase):
    
    portal_type = 'ATEvent'
    views = ('event_view', 'vcs_view', 'ics_view', )

tests.append(TestATEventFunctional)

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        for test in tests:
            suite.addTest(unittest.makeSuite(test))
        return suite
