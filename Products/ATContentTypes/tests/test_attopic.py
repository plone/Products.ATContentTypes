"""
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase

from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.public import *
from Products.ATContentTypes.tests.utils import dcEdit
import time

from Products.ATContentTypes.types.ATTopic import ATTopic
from Products.ATContentTypes.types.ATTopic import ATTopicSchema
#from Products.ATContentTypes.migration.ATCTMigrator import TopicMigrator
from Products.CMFTopic.Topic import Topic

tests = []

def editCMF(obj):
    dcEdit(obj)

def editATCT(obj):
    dcEdit(obj)

class TestSiteATTopic(atcttestcase.ATCTTypeTestCase):

    klass = ATTopic
    portal_type = 'ATTopic'
    cmf_portal_type = 'CMF Topic'
    cmf_klass = Topic
    title = 'Topic'
    meta_type = 'ATTopic'
    icon = 'topic_icon.gif'

    def test_edit(self):
        old = self._cmf
        new = self._ATCT
        editCMF(old)
        editATCT(new)
        self.failUnless(old.Title() == new.Title(), 'Title mismatch: %s / %s' \
                        % (old.Title(), new.Title()))
        self.failUnless(old.Description() == new.Description(), 'Description mismatch: %s / %s' \
                        % (old.Description(), new.Description()))


tests.append(TestSiteATTopic)

class TestATTopicFields(atcttestcase.ATCTFieldTestCase):

    def afterSetUp(self):
        atcttestcase.ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATTopic)

tests.append(TestATTopicFields)

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
