from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import PloneSiteLayer
from Products.PloneTestCase.setup import default_user
from Products.PloneTestCase.setup import default_password
from Products.PloneTestCase.setup import portal_name
from Products.PloneTestCase.setup import portal_owner
ZopeTestCase.installProduct('SiteAccess')
PloneTestCase.setupPloneSite()

import os

from zope.interface.verify import verifyObject

from Products.CMFCore.interfaces import IDublinCore
from Products.CMFCore.interfaces import IMutableDublinCore
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
from Products.Archetypes.atapi import AttributeStorage
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.atapi import IdWidget
from Products.Archetypes.atapi import RFC822Marshaller
from Products.Archetypes.atapi import MetadataStorage
from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.interfaces.base import IBaseContent
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.interfaces.referenceable import IReferenceable
from Products.Archetypes.interfaces.templatemixin import ITemplateMixin
from Products.Archetypes.tests.test_baseschema import BaseSchemaTest
from archetypes.referencebrowserwidget import ReferenceBrowserWidget

from plone.app.blob.markings import markAs

from Products.ATContentTypes.config import HAS_LINGUA_PLONE
from Products.ATContentTypes.interfaces import IATContentType
from Products.ATContentTypes.tests.utils import dcEdit
from Products.ATContentTypes.tests.utils import EmptyValidator
from Products.ATContentTypes.tests.utils import idValidator

test_home = os.path.dirname(__file__)

class ATCTSiteTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        # BBB - make sure we can regression test the deprecated ATBTreeFolder class
        user = self.portal.acl_users.getUserById(default_user)
        orig_roles = self.portal.acl_users.portal_role_manager.getRolesForPrincipal(user)
        self.setRoles(['Manager'])
        ttool = self.portal.portal_types
        cb_copy_data = ttool.manage_copyObjects(['Folder'])
        paste_data = ttool.manage_pasteObjects(cb_copy_data)
        temp_id = paste_data[0]['new_id']
        ttool.manage_renameObject(temp_id, 'Large Plone Folder')
        lpf = ttool['Large Plone Folder']
        lpf.title = 'Large Folder'
        lpf.product = 'ATContentTypes'
        lpf.content_meta_type = 'ATBTreeFolder'
        lpf.factory = 'addATBTreeFolder'
        self.setRoles(orig_roles)

class ATCTFunctionalSiteTestCase(PloneTestCase.FunctionalTestCase, ATCTSiteTestCase):
    pass

class ATCTTypeTestCase(ATCTSiteTestCase):
    """AT Content Types test

    Tests some basics of a type
    """

    klass = None
    portal_type = ''
    cmf_portal_type = ''
    title = ''
    meta_type = ''

    def afterSetUp(self):
        super(ATCTTypeTestCase, self).afterSetUp()
        self._ATCT = self._createType(self.folder, self.portal_type, 'ATCT')

    def _createType(self, context, portal_type, id, **kwargs):
        """Helper method to create a new type
        """
        ttool = getToolByName(context, 'portal_types')
        cat = self.portal.portal_catalog

        fti = ttool.getTypeInfo(portal_type)
        fti.constructInstance(context, id, **kwargs)
        obj = getattr(context.aq_inner.aq_explicit, id)
        cat.indexObject(obj)
        return obj

    def test_000testsetup(self):
        # test if we really have the right test setup
        # vars
        self.failUnless(self.klass)
        self.failUnless(self.portal_type)
        self.failUnless(self.title)
        self.failUnless(self.meta_type)

        # portal types
        self.failUnlessEqual(self._ATCT.portal_type, self.portal_type)

        # classes
        atct_class = self._ATCT.__class__
        self.failUnlessEqual(self.klass, atct_class)

    def test_dcEdit(self):
        new = self._ATCT
        dcEdit(new)

    def test_typeInfo(self):
        ti = self._ATCT.getTypeInfo()
        self.failUnlessEqual(ti.getId(), self.portal_type)
        self.failUnlessEqual(ti.Title(), self.title)

    def test_doesImplementDC(self):
        self.failUnless(verifyObject(IDublinCore, self._ATCT))
        self.failUnless(verifyObject(IMutableDublinCore, self._ATCT))

    def test_doesImplementATCT(self):
        self.failUnless(IATContentType.providedBy(self._ATCT))
        self.failUnless(verifyObject(IATContentType, self._ATCT))

    def test_doesImplementAT(self):
        self.failUnless(IBaseContent.providedBy(self._ATCT))
        self.failUnless(IReferenceable.providedBy(self._ATCT))
        self.failUnless(verifyObject(IBaseContent, self._ATCT))
        self.failUnless(verifyObject(IReferenceable, self._ATCT))

    def test_implementsTranslateable(self):
        # lingua plone is adding the ITranslatable interface to all types
        if not HAS_LINGUA_PLONE:
            return
        else:
            from Products.LinguaPlone.interfaces import ITranslatable
            self.failUnless(ITranslatable.providedBy(self._ATCT))
            self.failUnless(verifyObject(ITranslatable, self._ATCT))

    def test_not_implements_ITemplateMixin(self):
        self.failIf(ITemplateMixin.providedBy(self._ATCT))

    def test_implements_ISelectableBrowserDefault(self):
        iface = ISelectableBrowserDefault
        self.failUnless(iface.providedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

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

    def test_idValidation(self):
        self.setRoles(['Manager', 'Member']) # for ATTopic
        asdf = self._createType(self.folder, self.portal_type, 'asdf')
        self._createType(self.folder, self.portal_type, 'asdf2')
        self.setRoles(['Member'])

        request = self.app.REQUEST

        # invalid ids
        ids = ['asdf2', '???', '/asdf2', ' asdf2', 'portal_workflow',
            'portal_url']
        for id in ids:
            request.form = {'id':id, 'fieldset':'default'}
            self.assertNotEquals(asdf.validate(REQUEST=request), {}, "Not catched id: %s" % id)

        # valid ids
        ids = ['', 'abcd', 'blafasel']
        for id in ids:
            request.form = {'id':id}
            self.assertEquals(asdf.validate(REQUEST=request), {})

    def test_schema_marshall(self):
        atct = self._ATCT
        schema = atct.Schema()
        marshall = schema.getLayerImpl('marshall')
        marshallers = [RFC822Marshaller]
        try:
            from Products.Marshall import ControlledMarshaller
            marshallers.append(ControlledMarshaller)
        except ImportError:
            pass
        self.failUnless(isinstance(marshall, tuple(marshallers)), marshall)

    def beforeTearDown(self):
        self.logout()

class ATCTFieldTestCase(ATCTSiteTestCase, BaseSchemaTest):
    """ ATContentTypes test including AT schema tests """

    layer = PloneSiteLayer

    def afterSetUp(self):
        # initalize the portal but not the base schema test
        # because we want to overwrite the dummy and don't need it
        ATCTSiteTestCase.afterSetUp(self)
        self.setRoles(['Manager',])

    def createDummy(self, klass, id='dummy', subtype=None):
        portal = self.portal
        dummy = klass(oid=id)
        markAs(dummy, subtype)
        # put dummy in context of portal
        dummy = dummy.__of__(portal)
        portal.dummy = dummy
        dummy.initializeArchetype()
        return dummy

    def test_description(self):
        dummy = self._dummy
        field = dummy.getField('description')

        self.failUnless(ILayerContainer.providedBy(field))
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
        self.failUnlessEqual(field.read_permission, View)
        self.failUnlessEqual(field.write_permission, ModifyPortalContent)
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

        self.failUnless(ILayerContainer.providedBy(field))
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
        self.failUnlessEqual(field.read_permission, View)
        self.failUnlessEqual(field.write_permission, ModifyPortalContent)
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

        self.failUnless(ILayerContainer.providedBy(field))
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
        self.failUnlessEqual(field.read_permission, View)
        self.failUnlessEqual(field.write_permission, ModifyPortalContent)
        self.failUnlessEqual(field.generateMode, 'veVc')
        self.failUnlessEqual(field.force, '')
        self.failUnlessEqual(field.type, 'reference')
        self.failUnless(isinstance(field.storage, AttributeStorage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage())
        self.failUnlessEqual(field.validators, EmptyValidator)
        self.failUnless(isinstance(field.widget, ReferenceBrowserWidget))
        self.failUnless(field.widget.allow_sorting, u'field and widget need to enable sorting')
        self.failUnless(field.referencesSortable, u'field and widget need to enable sorting')

        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList))

