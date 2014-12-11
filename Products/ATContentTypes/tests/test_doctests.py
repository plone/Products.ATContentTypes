# -*- coding: UTF-8 -*-

FILES = [
    'events.txt', 'editing.txt',
    'topictool.txt', 'portaltype_criterion.txt', 'webdav.txt', 'http_access.txt',
    'reindex_sanity.txt', 'uploading.txt', 'browser_collection_views.txt',
    # traversal.txt registers the browser page "document_view", and this registration
    # stays active in different doctests, so we make sure to include it last.
    'traversal.txt',
]

import doctest
OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_NDIFF |
               doctest.REPORT_ONLY_FIRST_FAILURE)

from plone.testing import layered
from plone.app.testing.bbb import PTC_FUNCTIONAL_TESTING

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    for testfile in FILES:
        suite.addTest(layered(doctest.DocFileSuite(testfile,
                                optionflags=OPTIONFLAGS,
                                package="Products.ATContentTypes.tests",),
                      layer=PTC_FUNCTIONAL_TESTING)
                     )
    return suite
