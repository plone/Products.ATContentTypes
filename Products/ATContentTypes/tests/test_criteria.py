#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2005 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
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
import time

from Interface.Verify import verifyObject
from Products.Archetypes.interfaces.base import IBaseContent
from Products.Archetypes.interfaces.referenceable import IReferenceable
from Products.Archetypes.interfaces.metadata import IExtensibleMetadata

from Products.ATContentTypes.interfaces import IATTopicCriterion
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.interfaces import IATTopicSortCriterion

from Products.ATContentTypes.types.criteria.ATBaseCriterion import ATBaseCriterion
from Products.ATContentTypes.types.criteria.ATDateCriteria import \
    ATDateCriteria 
from Products.ATContentTypes.types.criteria.ATListCriterion import \
    ATListCriterion
from Products.ATContentTypes.types.criteria.ATSimpleIntCriterion import \
    ATSimpleIntCriterion
from Products.ATContentTypes.types.criteria.ATSimpleStringCriterion import \
    ATSimpleStringCriterion
from Products.ATContentTypes.types.criteria.ATPortalTypeCriterion import \
    ATPortalTypeCriterion
from Products.ATContentTypes.types.criteria.ATSortCriterion import \
    ATSortCriterion
from Products.ATContentTypes.types.criteria.ATSelectionCriterion import \
    ATSelectionCriterion
from Products.ATContentTypes.types.criteria.ATDateRangeCriterion import \
    ATDateRangeCriterion
from Products.ATContentTypes.types.criteria.ATReferenceCriterion import \
    ATReferenceCriterion
from Products.ATContentTypes.types.criteria.ATBooleanCriterion import \
    ATBooleanCriterion
tests = []

class CriteriaTest(atcttestcase.ATCTSiteTestCase):

    klass = None
    portal_type = None
    title = None
    meta_type = None

    def afterSetUp(self):
        atcttestcase.ATCTSiteTestCase.afterSetUp(self)
        self.dummy = self.createDummy(self.klass)

    def createDummy(self, klass, id='dummy'):
        folder = self.folder
        dummy = klass(id, 'dummyfield')
        # put dummy in context of portal
        folder._setObject(id, dummy)
        dummy = getattr(folder, id)
        dummy.initializeArchetype()
        return dummy

    def test_000testsetup(self):
        self.failUnless(self.klass)
        self.failUnless(self.portal_type)
        self.failUnless(self.title)
        self.failUnless(self.meta_type)
        
    def test_multipleCreateVariants(self):
        klass = self.klass
        id = 'dummy'
        field = 'dummyfield'
        
        dummy = klass(id, field)
        self.failUnless(dummy.getId(), id)
        self.failUnless(dummy.Field(), field)

        dummy = klass(id=id, field=field)
        self.failUnless(dummy.getId(), id)
        self.failUnless(dummy.Field(), field)

        dummy = klass(field, oid=id)
        self.failUnless(dummy.getId(), id)
        self.failUnless(dummy.Field(), field)

        dummy = klass(field=field, oid=id)
        self.failUnless(dummy.getId(), id)
        self.failUnless(dummy.Field(), field)
    
    def test_typeInfo(self):
        ti = self.dummy.getTypeInfo()
        self.failUnlessEqual(ti.getId(), self.portal_type)
        self.failUnlessEqual(ti.Title(), self.title)
        self.failUnlessEqual(ti.Metatype(), self.meta_type)
        
    def test_implements(self):
        self.failIf(IReferenceable.isImplementedBy(self.dummy))
        self.failIf(IExtensibleMetadata.isImplementedBy(self.dummy))
        self.failIf(self.dummy.isReferenceable)
        self.failUnless(IBaseContent.isImplementedBy(self.dummy))
        self.failUnless(IATTopicCriterion.isImplementedBy(self.dummy))
        self.failUnless(verifyObject(IBaseContent, self.dummy))
        self.failUnless(verifyObject(IATTopicCriterion, self.dummy))
        

class TestATBaseCriterion(CriteriaTest):
    klass = ATBaseCriterion
    title = 'Base Criterion'
    meta_type = 'ATBaseCriterion'
    portal_type = 'ATBaseCriterion'

    def test_typeInfo(self):
        # not registered
        pass

tests.append(TestATBaseCriterion)


class TestATDateCriteria(CriteriaTest):
    klass = ATDateCriteria
    title = 'Friendly Date Criteria'
    meta_type = 'ATFriendlyDateCriteria'
    portal_type = 'ATDateCriteria'

tests.append(TestATDateCriteria)


class TestATListCriterion(CriteriaTest):
    klass = ATListCriterion
    title = 'List Criterion'
    meta_type = 'ATListCriterion'
    portal_type = 'ATListCriterion'

tests.append(TestATListCriterion)


class TestATSimpleIntCriterion(CriteriaTest):
    klass = ATSimpleIntCriterion
    title = 'Simple Int Criterion'
    meta_type = 'ATSimpleIntCriterion'
    portal_type = 'ATSimpleIntCriterion'

tests.append(TestATSimpleIntCriterion)


class TestATSimpleStringCriterion(CriteriaTest):
    klass = ATSimpleStringCriterion
    title = 'Simple String Criterion'
    meta_type = 'ATSimpleStringCriterion'
    portal_type = 'ATSimpleStringCriterion'

tests.append(TestATSimpleStringCriterion)


class TestATSortCriterion(CriteriaTest):
    klass = ATSortCriterion
    title = 'Sort Criterion'
    meta_type = 'ATSortCriterion'
    portal_type = 'ATSortCriterion'

tests.append(TestATSortCriterion)


class TestATSelectionCriterion(CriteriaTest):
    klass = ATSelectionCriterion
    title = 'Selection Criterion'
    meta_type = 'ATSelectionCriterion'
    portal_type = 'ATSelectionCriterion'

tests.append(TestATSelectionCriterion)


class TestATDateRangeCriterion(CriteriaTest):
    klass = ATDateRangeCriterion
    title = 'Date Range Criterion'
    meta_type = 'ATDateRangeCriterion'
    portal_type = 'ATDateRangeCriterion'

tests.append(TestATDateRangeCriterion)


class TestATReferenceCriterion(CriteriaTest):
    klass = ATReferenceCriterion
    title = 'Reference Criterion'
    meta_type = 'ATReferenceCriterion'
    portal_type = 'ATReferenceCriterion'

tests.append(TestATReferenceCriterion)


class TestATBooleanCriterion(CriteriaTest):
    klass = ATBooleanCriterion
    title = 'Boolean Criterion'
    meta_type = 'ATBooleanCriterion'
    portal_type = 'ATBooleanCriterion'

tests.append(TestATBooleanCriterion)


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
