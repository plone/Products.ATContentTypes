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
ZopeTestCase.installProduct('ATContentTypes')
ZopeTestCase.installProduct('ATReferenceBrowserWidget')
from Products.ATContentTypes.config import INSTALL_LINGUA_PLONE
if INSTALL_LINGUA_PLONE and ZopeTestCase.hasProduct('LinguaPlone'):
    ZopeTestCase.installProduct('PloneLanguageTool')
    ZopeTestCase.installProduct('LinguaPlone')

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
from Products.Archetypes.tests.test_baseschema import BaseSchemaTest
from Products.ATContentTypes.config import HAS_LINGUA_PLONE
from Products.ATContentTypes.interfaces import IATContentType
from Products.ATContentTypes.tests.utils import dcEdit
from Products.ATContentTypes.tests.utils import EmptyValidator
from Products.ATContentTypes.tests.utils import idValidator
from Products.ATContentTypes.tests.utils import FakeRequestSession
from Products.ATContentTypes.tests.utils import DummySessionDataManager
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
# BBB remove import from PloneLanguageTool later
try:
    from Products.CMFPlone.interfaces.Translatable import ITranslatable
except ImportError:
    from Products.PloneLanguageTool.interfaces import ITranslatable

from Products.ATContentTypes.config import ATCT_PORTAL_TYPE

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
        self.portal_type = ATCT_PORTAL_TYPE(self.portal_type)
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
        atctFTI.constructInstance(self.folder, 'asdf')
        atctFTI.constructInstance(self.folder, 'asdf2')
        asdf = self.folder.asdf
        
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
        #XXX self.failUnlessEqual(tuple(vocab), ())

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
        self.failUnless(len(tuple(vocab)) >= 2, tuple(vocab))
        self.failUnless('base_view' in tuple(vocab), tuple(vocab))

from Products.Archetypes.tests.atsitetestcase import ATFunctionalSiteTestCase
from Products.Archetypes.tests.attestcase import default_user
from Products.Archetypes.tests.atsitetestcase import portal_owner
import time

class ATCTFuncionalTestCase(ATFunctionalSiteTestCase):
    """Integration tests for view and edit templates
    """
    
    portal_type = None
    views = ()

    def afterSetUp(self):
        self.portal_type = ATCT_PORTAL_TYPE(self.portal_type)
        # Put dummy sdm and dummy SESSION object into REQUEST
        request = self.app.REQUEST
        self.app._setObject('session_data_manager', DummySessionDataManager())
        sdm = self.app.session_data_manager
        request.set('SESSION', sdm.getSessionData())
        
        # basic data
        self.folder_url = self.folder.absolute_url()
        self.folder_path = '/%s' % self.folder.absolute_url(1)
        self.basic_auth = '%s:secret' % default_user
        self.owner_auth = '%s:secret' % portal_owner
        
        # We want 401 responses, not redirects to a login page
        self.portal._delObject('cookie_authentication')
        
        # create test object
        self.obj_id = 'test_object'
        self.folder.invokeFactory(self.portal_type, self.obj_id, title=self.obj_id)
        self.obj = getattr(self.folder.aq_explicit, self.obj_id)
        self.obj_url = self.obj.absolute_url()
        self.obj_path = '/%s' % self.obj.absolute_url(1)
        
        # error log
        from Products.SiteErrorLog.SiteErrorLog import temp_logs
        temp_logs = {} # clean up log
        self.error_log = self.getPortal().error_log
        self.error_log._ignored_exceptions = ()

    def assertStatusEqual(self, a, b, msg=''):
        """Helper method that uses the error log to output useful debug infos
        """
        now = time.time()
        if a != b:
            entries = self.error_log.getLogEntries()
            if entries:
                msg = entries[0]['tb_text']
            else:
                if not msg:
                    msg = 'no error log msg available'
        self.failUnlessEqual(a, b, msg)
        
    def test_createObject(self):
        # create an object using the createObject script
        response = self.publish(self.folder_path +
                                '/createObject?type_name=%s' % self.portal_type,
                                self.basic_auth)

        self.assertStatusEqual(response.getStatus(), 302) # Redirect to edit

        # omit ?portal_status_message=...
        body = response.getBody().split('?')[0]
        
        self.failUnless(body.startswith(self.folder_url), body)
        self.failUnless(body.endswith('/atct_edit'), body)

        # Perform the redirect
        edit_form_path = body[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(edit_form_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK

    def test_edit_view(self):
        # edit should work        
        response = self.publish('%s/atct_edit' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK

    def test_metadata_edit_view(self):
        # metadata edit should work
        response = self.publish('%s/base_metadata' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK

    def test_base_view(self):
        # base view should work
        response = self.publish('%s/base_view' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK

    def test_templatemixin_view(self):
        # template mixin magic should work
        # XXX more tests?
        response = self.publish('%s/view' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK

    def test_local_sharing_view(self):
        # sharing tab should work
        # XXX security tests?
        response = self.publish('%s/folder_localrole_form' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK    

    def test_workflow_view(self):
        # workflow tab should work
        response = self.publish('%s/content_status_history' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK
        
    def test_linguaplone_views(self):
        if not HAS_LINGUA_PLONE:
            return
        
        response = self.publish('%s/translate_item' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK
        response = self.publish('%s/manage_translations_form' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK

    def test_linguaplone_create_translation(self):
        if not HAS_LINGUA_PLONE:
            return
        
        # create translation creates a new object
        response = self.publish('%s/createTranslation?language=de&set_language=de' 
                                 % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 302) # Redirect

        # omit ?portal_status_message=...
        body = response.getBody().split('?')[0]
        
        self.failUnless(body.startswith(self.folder_url))
        self.failUnless(body.endswith('/translate_item'))

        # Perform the redirect
        form_path = body[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(form_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK
        
        translated_id = "%s-de" % self.obj_id
        self.failUnless(translated_id in self.folder.objectIds(),
                        self.folder.objectIds())
    
    def test_additional_view(self):
        # additional views:
        for view in self.views:
            response = self.publish('%s/%s' % (self.obj_path, view), self.basic_auth)
            self.assertStatusEqual(response.getStatus(), 200, 
                "%s: %s" % (view, response.getStatus())) # OK
                
    def test_discussion(self):
        # enable discussion for  the type
        ttool = getToolByName(self.portal, 'portal_types')
        ttool[self.portal_type].allow_discussion = True
        
        response = self.publish('%s/discussion_reply_form' 
                                 % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # ok
        
        response = self.publish('%s/discussion_reply?subject=test&body_text=testbody' 
                                 % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 302) # Redirect
        
        # omit ?portal_status_message=...
        body = response.getBody().split('?')[0]
        
        self.failUnless(body.startswith(self.folder_url))
        
        # Perform the redirect
        form_path = body[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(form_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK
        
        self.failUnless(hasattr(self.obj.aq_explicit, 'talkback'))


from Products.CMFCore.utils import getToolByName
from Products.CMFQuickInstallerTool.QuickInstallerTool import AlreadyInstalled
from Products.Archetypes.tests.atsitetestcase import portal_name
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

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
