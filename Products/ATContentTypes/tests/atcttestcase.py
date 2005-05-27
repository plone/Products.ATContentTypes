# -*- coding: latin1 -*- 
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
"""Common imports and declarations

common includes a set of basic things that every test needs. Ripped of from my
Archetypes test suit


"""

__author__ = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'

###
# general test suits including products
###

from Testing import ZopeTestCase
ZopeTestCase.installProduct('ATContentTypes')
ZopeTestCase.installProduct('ATReferenceBrowserWidget')

import os

from Products.Archetypes.tests.attestcase import ATTestCase
from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase

from Interface.Verify import verifyObject
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.interfaces.DublinCore import DublinCore as IDublinCore
from Products.CMFCore.interfaces.DublinCore import MutableDublinCore as IMutableDublinCore
from Products.Archetypes.interfaces.base import IBaseContent
from Products.Archetypes.public import *
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.interfaces.referenceable import IReferenceable
from Products.Archetypes.interfaces.templatemixin import ITemplateMixin
from Products.Archetypes.tests.test_baseschema import BaseSchemaTest
from Products.ATContentTypes.config import HAS_PLONE2
from Products.ATContentTypes.config import HAS_LINGUA_PLONE
from Products.ATContentTypes import permission as ATCTPermissions
from Products.ATContentTypes.interfaces import IATContentType
from Products.ATContentTypes.tests.utils import dcEdit
from Products.ATContentTypes.tests.utils import EmptyValidator
from Products.ATContentTypes.tests.utils import idValidator
from Products.ATContentTypes.tests.utils import FakeRequestSession
from Products.ATContentTypes.tests.utils import DummySessionDataManager
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.CMFCore.utils import getToolByName
from Testing.ZopeTestCase.functional import Functional

# BBB remove import from PloneLanguageTool later
try:
    from Products.CMFPlone.interfaces.Translatable import ITranslatable
except ImportError:
    from Products.PloneLanguageTool.interfaces import ITranslatable

test_home = os.path.dirname(__file__) 

class ATCTSiteTestCase(ATSiteTestCase):
    pass

class ATCTFunctionalSiteTestCase(Functional, ATCTSiteTestCase):
    __implements__ = Functional.__implements__ + ATCTSiteTestCase.__implements__    

class ATCTTypeTestCase(ATSiteTestCase):
    """AT Content Types test
    
    Tests some basics of a type
    """

    klass = None
    cmf_klass = None
    portal_type = ''
    cmf_portal_type = ''
    title = ''
    meta_type = ''
    icon = ''

    def afterSetUp(self):
        self.setRoles(['Manager', 'Member'])
        self._ATCT = self._createType(self.folder, self.portal_type, 'ATCT')
        self._cmf = self._createType(self.folder, self.cmf_portal_type, 'cmf')

    def _createType(self, context, portal_type, id):
        """Helper method to create a new type 
        """
        ttool = getToolByName(context, 'portal_types')
        fti = ttool.getTypeInfo(portal_type)
        fti.constructInstance(context, id)
        return getattr(context.aq_inner.aq_explicit, id)
    
    def test_000testsetup(self):
        # test if we really have the right test setup
        # vars
        self.failUnless(self.klass)
        self.failUnless(self.cmf_klass)
        self.failUnless(self.portal_type)
        self.failUnless(self.cmf_portal_type)
        self.failUnless(self.title)
        self.failUnless(self.meta_type)
        self.failUnless(self.icon)
        
        # portal types
        self.failUnlessEqual(self._ATCT.portal_type, self.portal_type)
        self.failUnlessEqual(self._cmf.portal_type, self.cmf_portal_type)
        
        # classes
        atct_class = self._ATCT.__class__
        cmf_class = self._cmf.__class__
        self.failUnlessEqual(self.klass, atct_class)
        self.failUnlessEqual(self.cmf_klass, cmf_class)

    def test_dcEdit(self):
        #if not hasattr(self, '_cmf') or not hasattr(self, '_ATCT'):
        #    return
        old = self._cmf
        new = self._ATCT
        dcEdit(old)
        dcEdit(new)
        self.compareDC(old, new)

    def test_typeInfo(self):
        ti = self._ATCT.getTypeInfo()
        self.failUnlessEqual(ti.getId(), self.portal_type)
        self.failUnlessEqual(ti.Title(), self.title)
        self.failUnlessEqual(ti.getIcon(), self.icon)
        self.failUnlessEqual(ti.Metatype(), self.meta_type)

    def test_doesImplemendDC(self):
        self.failUnless(IDublinCore.isImplementedBy(self._ATCT))
        self.failUnless(IMutableDublinCore.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(IDublinCore, self._ATCT))
        self.failUnless(verifyObject(IMutableDublinCore, self._ATCT))

    def test_doesImplementATCT(self):
        self.failUnless(IATContentType.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(IATContentType, self._ATCT))
        
    def test_doesImplementAT(self):
        self.failUnless(IBaseContent.isImplementedBy(self._ATCT))
        self.failUnless(IReferenceable.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(IBaseContent, self._ATCT))
        self.failUnless(verifyObject(IReferenceable, self._ATCT))
        
    def test_implementsTranslateable(self):
        # lingua plone is adding the ITranslatable interface to all types
        if not HAS_LINGUA_PLONE:
            return
        self.failUnless(ITranslatable.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(ITranslatable, self._ATCT)) 
        
    def test_implementsITemplateMixin(self):
        self.failUnless(ITemplateMixin.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(ITemplateMixin, self._ATCT))
    
    def test_implementsSelectableBrowserDefault(self):
        if not HAS_PLONE2:
            return
        from Products.CMFPlone.interfaces.BrowserDefault \
            import ISelectableBrowserDefault   
        self.failUnless(ISelectableBrowserDefault.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(ISelectableBrowserDefault, self._ATCT))

    def compareDC(self, first, second=None, **kwargs):
        """
        """
        if second != None:
            title = second.Title()
            description = second.Description()
        else:
            title = kwargs.get('title')
            description = kwargs.get('description')

        self.failUnlessEqual(first.Title(), title)
        self.failUnlessEqual(first.Description(), description)
        # XXX more

    def compareAfterMigration(self, migrated, mod=None, created=None):
        self.failUnless(isinstance(migrated, self.klass),
                        migrated.__class__)
        self.failUnlessEqual(migrated.getTypeInfo().getId(), self.portal_type)
        self.failUnlessEqual(migrated.ModificationDate(), mod)
        self.failUnlessEqual(migrated.CreationDate(), created)


    def test_idValidation(self):
        ttool = getToolByName(self.portal, 'portal_types')
        atctFTI = ttool.getTypeInfo(self.portal_type)
        atctFTI.constructInstance(self.folder, 'asdf')
        atctFTI.constructInstance(self.folder, 'asdf2')
        asdf = self.folder.asdf
        
        request = FakeRequestSession()
        
        # invalid ids
        ids = ['asdf2', 'äää', '/asdf2', ' asdf2', 'portal_workflow',
            'portal_url']
        for id in ids:
            request.form = {'id':id, 'fieldset':'default'}
            self.assertNotEquals(asdf.validate(REQUEST=request), {}, "Not catched id: %s" % id)

        # valid ids
        ids = ['', 'abcd', 'blafasel']
        for id in ids:
            request.form = {'id':id}
            self.assertEquals(asdf.validate(REQUEST=request), {})

    def test_getobjpositioninparent(self):
        # TODO: not a real test
        self._ATCT.getObjPositionInParent()

    def beforeTearDown(self):
        self.logout()

class ATCTFieldTestCase(BaseSchemaTest):
    """ ATContentTypes test including AT schema tests """
    
    def afterSetUp(self):
        # initalize the portal but not the base schema test
        # because we want to overwrite the dummy and don't need it
        ATSiteTestCase.afterSetUp(self)
        self.setRoles(['Manager',])

    def createDummy(self, klass, id='dummy'):
        portal = self.portal
        dummy = klass(oid=id)
        # put dummy in context of portal
        dummy = dummy.__of__(portal)
        portal.dummy = dummy
        dummy.initializeArchetype()
        return dummy

    def test_description(self):
        dummy = self._dummy
        field = dummy.getField('description')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.required, False)
        self.failUnlessEqual(field.default, '')
        self.failUnlessEqual(field.searchable, True)
        self.failUnlessEqual(field.primary, False)
        vocab = field.vocabulary
        self.failUnlessEqual(vocab, ())
        self.failUnlessEqual(field.enforceVocabulary, False)
        self.failUnlessEqual(field.multiValued, False)
        self.failUnlessEqual(field.isMetadata, True)
        self.failUnlessEqual(field.accessor, 'Description')
        self.failUnlessEqual(field.mutator, 'setDescription')
        self.failUnlessEqual(field.edit_accessor, 'getRawDescription')
        self.failUnlessEqual(field.read_permission, CMFCorePermissions.View)
        self.failUnlessEqual(field.write_permission,
                             CMFCorePermissions.ModifyPortalContent)
        self.failUnlessEqual(field.generateMode, 'mVc')
        #self.failUnless(field.generateMode == 'veVc', field.generateMode)
        self.failUnlessEqual(field.force, '')
        self.failUnlessEqual(field.type, 'text')
        self.failUnless(isinstance(field.storage, MetadataStorage))
        self.failUnless(field.getLayerImpl('storage') == MetadataStorage())
        self.failUnlessEqual(field.validators, EmptyValidator)
        self.failUnless(isinstance(field.widget, TextAreaWidget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList))
        self.failUnlessEqual(tuple(vocab), ())

    def test_id(self):
        dummy = self._dummy
        field = dummy.getField('id')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.required, False)
        self.failUnlessEqual(field.default, None)
        self.failUnlessEqual(field.searchable, True)
        self.failUnlessEqual(getattr(field, 'primary', None), None)
        vocab = field.vocabulary
        self.failUnlessEqual(vocab, ())
        self.failUnlessEqual(field.enforceVocabulary, False)
        self.failUnlessEqual(field.multiValued, False)
        self.failUnlessEqual(field.isMetadata, False)
        self.failUnlessEqual(field.accessor, 'getId')
        self.failUnlessEqual(field.mutator, 'setId')
        self.failUnlessEqual(field.edit_accessor, 'getRawId')
        self.failUnlessEqual(field.read_permission, CMFCorePermissions.View)
        self.failUnlessEqual(field.write_permission,
                             CMFCorePermissions.ModifyPortalContent)
        self.failUnlessEqual(field.generateMode, 'veVc')
        self.failUnlessEqual(field.force, '')
        self.failUnlessEqual(field.type, 'string')
        self.failUnless(isinstance(field.storage, AttributeStorage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage())
        self.failUnlessEqual(field.validators, idValidator)
        self.failUnless(isinstance(field.widget, IdWidget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList))
        self.failUnlessEqual(tuple(vocab), ())

    def test_relateditems(self):
        dummy = self._dummy
        field = dummy.getField('relatedItems')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.required, False)
        self.failUnlessEqual(field.default, None)
        self.failUnlessEqual(field.searchable, False)
        self.failUnlessEqual(getattr(field, 'primary', None), None)
        vocab = field.vocabulary
        self.failUnlessEqual(vocab, ())
        self.failUnlessEqual(field.enforceVocabulary, False)
        self.failUnlessEqual(field.multiValued, True)
        self.failUnlessEqual(field.isMetadata, True)
        self.failUnlessEqual(field.accessor, 'getRelatedItems')
        self.failUnlessEqual(field.mutator, 'setRelatedItems')
        self.failUnlessEqual(field.edit_accessor, 'getRawRelatedItems')
        self.failUnlessEqual(field.read_permission, CMFCorePermissions.View)
        self.failUnlessEqual(field.write_permission,
                             CMFCorePermissions.ModifyPortalContent)
        self.failUnlessEqual(field.generateMode, 'veVc')
        self.failUnlessEqual(field.force, '')
        self.failUnlessEqual(field.type, 'reference')
        self.failUnless(isinstance(field.storage, AttributeStorage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage())
        self.failUnlessEqual(field.validators, EmptyValidator)
        self.failUnless(isinstance(field.widget, ReferenceBrowserWidget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList))

    def test_layout(self):
        dummy = self._dummy
        field = dummy.getField('layout')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.required, False)
        self.failUnlessEqual(field.default, '')
        self.failUnlessEqual(field.searchable, False)
        self.failUnlessEqual(getattr(field, 'primary', None), None)
        vocab = field.vocabulary
        self.failUnlessEqual(vocab, 'getAvailableLayouts')
        self.failUnlessEqual(field.enforceVocabulary, False)
        self.failUnlessEqual(field.multiValued, False)
        self.failUnlessEqual(field.isMetadata, False)
        self.failUnlessEqual(field.accessor, 'getLayout')
        self.failUnlessEqual(field.mutator, 'setLayout')
        self.failUnlessEqual(field.edit_accessor, 'getRawLayout')
        self.failUnlessEqual(field.default_method, "getDefaultLayout")
        self.failUnlessEqual(field.read_permission, CMFCorePermissions.View)
        self.failUnlessEqual(field.write_permission,
                             ATCTPermissions.ModifyViewTemplate)
        self.failUnlessEqual(field.generateMode, 'veVc')
        self.failUnlessEqual(field.force, '')
        self.failUnlessEqual(field.type, 'string')
        self.failUnless(isinstance(field.storage, AttributeStorage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage())
        self.failUnlessEqual(field.validators, EmptyValidator)
        self.failUnless(isinstance(field.widget, SelectionWidget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList))
        self.failUnless(len(tuple(vocab)) >= 1, tuple(vocab))

from Products.CMFQuickInstallerTool.QuickInstallerTool import AlreadyInstalled
from Products.Archetypes.tests.atsitetestcase import portal_name
from Products.Archetypes.tests.atsitetestcase import portal_owner
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
import time

def setupATCT(app, id=portal_name, quiet=False):
    get_transaction().begin()
    _start = time.time()
    portal = app[id]
    if not quiet: ZopeTestCase._print('Adding ATContentTypes \n')

    # login as manager
    user = app.acl_users.getUserById(portal_owner).__of__(app.acl_users)
    newSecurityManager(None, user)
    # add ATCT
    qi = getToolByName(portal, 'portal_quickinstaller') 
    try:
        qi.installProduct('ATReferenceBrowserWidget')
    except AlreadyInstalled:
        # EAFP = easier ask for forgiveness than permission
        if not quiet: ZopeTestCase._print('ATReferenceBrowserWidget already installed ...\n')
    try:
        qi.installProduct('ATContentTypes')
    except AlreadyInstalled:
        if not quiet: ZopeTestCase._print('ATContentTypes already installed ...\n')

    # Log out
    noSecurityManager()
    get_transaction().commit()
    if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

app = ZopeTestCase.app()
setupATCT(app)
ZopeTestCase.close(app)
