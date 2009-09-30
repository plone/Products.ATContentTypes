from unittest import TestSuite
from plone.app.blob.tests import bbb
from Products.PloneTestCase import PloneTestCase


# while the following test case is emtpty, it takes care of setting up a
# blob-aware zodb for testing against blobs

class BlobSetupTestCase(PloneTestCase.PloneTestCase):

    layer = bbb.plone


def test_suite():
    return TestSuite()
