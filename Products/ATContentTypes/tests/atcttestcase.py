"""Common imports and declarations

common includes a set of basic things that every test needs. Ripped of from my
Archetypes test suit


"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

###
# general test suits including products
###

from Testing import ZopeTestCase
from Products.Archetypes.tests.attestcase import ATTestCase
from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase
from Products.ATContentTypes.config import INSTALL_LINGUA_PLONE

## sessions are required for functional tests
ZopeTestCase.utils.setupCoreSessions()

ZopeTestCase.installProduct('ATContentTypes')
ZopeTestCase.installProduct('ATReferenceBrowserWidget')

if INSTALL_LINGUA_PLONE and ZopeTestCase.hasProduct('LinguaPlone'):
    ZopeTestCase.installProduct('PloneLanguageTool')
    ZopeTestCase.installProduct('LinguaPlone')

from Interface.Verify import verifyObject
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.interfaces.DublinCore import DublinCore as IDublinCore
from Products.CMFCore.interfaces.DublinCore import MutableDublinCore as IMutableDublinCore
from Products.Archetypes.interfaces.base import IBaseContent
from Products.Archetypes.public import *
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.interfaces.referenceable import IReferenceable
from Products.Archetypes.tests.test_baseschema import BaseSchemaTest
from Products.ATContentTypes.interfaces import IATContentType
from Products.ATContentTypes.tests.utils import dcEdit
from Products.ATContentTypes.tests.utils import EmptyValidator
from Products.ATContentTypes.tests.utils import idValidator
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from UserDict import UserDict

class FakeRequestSession(UserDict):
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')
    security.declareObjectPublic()
    
    def set(self, key, value):
        self[key] = value

InitializeClass(FakeRequestSession)

class ATCTSiteTestCase(ATSiteTestCase):
    pass

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

    def compareDC(self, first, second=None, **kwargs):
        """
        """
        if second:
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
        atctFTI.constructInstance(self.portal, 'asdf')
        atctFTI.constructInstance(self.portal, 'asdf2')
        asdf = self.portal.asdf
        
        request = FakeRequestSession()
        
        # invalid ids
        ids = ['asdf2', 'ההה', '/asdf2', ' asdf2', 'portal_workflow',
            'portal_url']
        for id in ids:
            request.form = {'id':id, 'fieldset':'default'}
            self.assertNotEquals(asdf.validate(REQUEST=request), {}, "Not catched id: %s" % id)

        # valid ids
        ids = ['', 'abcd', 'blafasel']
        for id in ids:
            request.form = {'id':id}
            self.assertEquals(asdf.validate(REQUEST=request), {})

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
        self.failUnlessEqual(tuple(vocab), ())

    def test_layout(self):
        dummy = self._dummy
        field = dummy.getField('layout')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.required, False)
        self.failUnlessEqual(field.default, '')
        self.failUnlessEqual(field.searchable, False)
        self.failUnlessEqual(getattr(field, 'primary', None), None)
        vocab = field.vocabulary
        self.failUnlessEqual(vocab, '_voc_templates')
        self.failUnlessEqual(field.enforceVocabulary, False)
        self.failUnlessEqual(field.multiValued, False)
        self.failUnlessEqual(field.isMetadata, False)
        self.failUnlessEqual(field.accessor, 'getLayout')
        self.failUnlessEqual(field.mutator, 'setLayout')
        self.failUnlessEqual(field.edit_accessor, 'getRawLayout')
        self.failUnlessEqual(field.default_method, "getDefaultLayout")
        self.failUnlessEqual(field.read_permission, CMFCorePermissions.View)
        self.failUnlessEqual(field.write_permission,
                             CMFCorePermissions.ManagePortal)
        self.failUnlessEqual(field.generateMode, 'veVc')
        self.failUnlessEqual(field.force, '')
        self.failUnlessEqual(field.type, 'string')
        self.failUnless(isinstance(field.storage, AttributeStorage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage())
        self.failUnlessEqual(field.validators, EmptyValidator)
        self.failUnless(isinstance(field.widget, SelectionWidget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList))
        self.failUnless(len(tuple(vocab)) >= 2)
        self.failUnless('base_view' in tuple(vocab))

from Products.Archetypes.tests.atsitetestcase import ATFunctionalSiteTestCase
from Products.Archetypes.tests.attestcase import default_user

class ATCTFuncionalTestCase(ATFunctionalSiteTestCase):
    """Integration tests for view and edit templates
    """
    
    portal_type = None
    views = ()

    def afterSetUp(self):
        # Put SESSION object into REQUEST
        request = self.app.REQUEST
        ##sdm = self.app.session_data_manager
        ##request.set('SESSION', sdm.getSessionData())
        request.set('SESSION', FakeRequestSession())
            
        self.folder_url = self.folder.absolute_url()
        self.folder_path = '/%s' % self.folder.absolute_url(1)
        self.basic_auth = '%s:secret' % default_user
        # We want 401 responses, not redirects to a login page
        self.portal._delObject('cookie_authentication')
        
    def test_createObject(self):
        # create an object using the createObject script
        response = self.publish(self.folder_path +
                                '/createObject?type_name=%s' % self.portal_type,
                                self.basic_auth)

        self.assertEqual(response.getStatus(), 302) # Redirect to edit

        # omit ?portal_status_message=...
        body = response.getBody().split('?')[0]
        
        self.failUnless(body.startswith(self.folder_url))
        self.failUnless(body.endswith('/atct_edit'))

        # Perform the redirect
        edit_form_path = body[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(edit_form_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200) # OK

    def test_views(self):
        obj_id = 'test_object'
        self.folder.invokeFactory(self.portal_type, obj_id, title=obj_id)
        obj = getattr(self.folder.aq_explicit, obj_id)
        obj_url = obj.absolute_url()
        obj_path = '/%s' % obj.absolute_url(1)

        # edit should work        
        response = self.publish('%s/atct_edit' % obj_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200) # OK

        # metadata edit should work
        response = self.publish('%s/base_metadata' % obj_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200) # OK

        # base view should work
        response = self.publish('%s/base_view' % obj_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200) # OK
    
        # additional views:
        for view in self.views:
            response = self.publish('%s/%s' % (obj_path, view), self.basic_auth)
            self.assertEqual(response.getStatus(), 200) # OK

from Products.CMFCore.utils import getToolByName
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
    if not quiet: ZopeTestCase._print('Installing ATContentTypes ... ')

    # login as manager
    user = app.acl_users.getUserById(portal_owner).__of__(app.acl_users)
    newSecurityManager(None, user)
    # add ATCT
    qi = getToolByName(portal, 'portal_quickinstaller') 
    try:
        qi.installProduct('ATReferenceBrowserWidget')
    except AlreadyInstalled:
        # EAFP = easier ask for forgiveness than permission
        if not quiet: ZopeTestCase._print('ATReferenceBrowserWidget already installed ... ')
    try:
        qi.installProduct('ATContentTypes')
    except AlreadyInstalled:
        if not quiet: ZopeTestCase._print('ATContentTypes already installed ... ')

    #if isSwitchedToATCT(portal):
    #    # XXX right now ATCT unit tests don't run in ATCT mode.
    #    # Switching to native mode
    #    ZopeTestCase._print('switching to CMF mode ... ')
    #    portal.switchATCT2CMF()

    # Log out
    noSecurityManager()
    get_transaction().commit()
    if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

app = ZopeTestCase.app()
setupATCT(app)
ZopeTestCase.close(app)
