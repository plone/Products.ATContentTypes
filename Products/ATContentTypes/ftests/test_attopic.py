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

class TestATTopicFunctional(atctftestcase.ATCTIntegrationTestCase):

    def afterSetUp(self):
        # adding topics is restricted
        self.setRoles(['Manager', 'Member',])
        atctftestcase.ATCTIntegrationTestCase.afterSetUp(self)
        
    def test_templatemixin_view_without_view(self):
        # template mixin magic should work
        # XXX more tests?
        response = self.publish('%s/' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) #
    
    portal_type = 'ATTopic'
    views = ('atct_topic_view', 'criterion_edit_form', 'atct_topic_subtopics')

tests.append(TestATTopicFunctional)

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
