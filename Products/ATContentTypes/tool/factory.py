from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_base, aq_inner
from App.Common import package_home
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.ATContentTypes.config import GLOBALS
from Products.ATContentTypes.interfaces import IFactoryTool
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.TempFolder import TempFolder
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ZPublisher.Publish import call_object, missing_name, dont_publish_class
from ZPublisher.mapply import mapply
from zExceptions import NotFound
from zope.interface import implements
from zope.structuredtext import stx2html
import os

FACTORY_INFO = '__factory__info__'


def _createObjectByType(type_name, container, id, *args, **kw):
    """This function replaces Products.CMFPlone.utils._createObjectByType.

    If no product is set on fti, use IFactory to lookup the factory.
    Additionally we add 'container' as 'parent' kw argument when calling the
    IFactory implementation. this ensures the availability of the acquisition
    chain if needed inside the construction logic.

    The kw argument hack is some kind of semi-valid since the IFactory
    interface promises the __call__ function to accept all given args and kw
    args. As long as the specific IFactory implementation provides this
    signature everything works well unless any other 3rd party factory expects
    another kind of object as 'parent' kw arg than the provided one.
    """
    id = str(id)
    typesTool = getToolByName(container, 'portal_types')
    fti = typesTool.getTypeInfo(type_name)
    if not fti:
        raise ValueError('Invalid type %s' % type_name)

    if not fti.product:
        kw['parent'] = container

    return fti._constructInstance(container, id, *args, **kw)


class FactoryTool(PloneBaseTool, UniqueObject, SimpleItem):
    """ """
    id = 'portal_factory'
    meta_type = 'Plone Factory Tool'
    toolicon = 'skins/plone_images/add_icon.png'
    security = ClassSecurityInfo()
    isPrincipiaFolderish = 0

    implements(IFactoryTool, IHideFromBreadcrumbs)

    manage_options = (
        ({'label': 'Overview', 'action': 'manage_overview'},
         {'label': 'Documentation', 'action': 'manage_docs'},
         {'label': 'Factory Types', 'action': 'manage_portal_factory_types'}) +
        SimpleItem.manage_options)

    wwwpath = os.path.join(package_home(GLOBALS), 'www')

    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile(
        os.path.join(wwwpath, 'portal_factory_manage_overview'),
        globals()
    )
    manage_overview.__name__ = 'manage_overview'
    manage_overview._need__name__ = 0

    security.declareProtected(ManagePortal, 'manage_portal_factory_types')
    manage_portal_factory_types = PageTemplateFile(
        os.path.join(wwwpath, 'portal_factory_manage_types'),
        globals()
    )
    manage_portal_factory_types.__name__ = 'manage_portal_factory_types'
    manage_portal_factory_types._need__name__ = 0

    manage_main = manage_overview

    security.declareProtected(ManagePortal, 'manage_docs')
    manage_docs = PageTemplateFile(
        os.path.join(wwwpath, 'portal_factory_manage_docs'),
        globals()
    )
    manage_docs.__name__ = 'manage_docs'

    with open(os.path.join(wwwpath, 'portal_factory_docs.stx'), 'r') as f:
        _docs = stx2html(f.read())

    security.declarePublic('docs')

    def docs(self):
        """Returns FactoryTool docs formatted as HTML"""
        return self._docs

    def getFactoryTypes(self):
        if not hasattr(self, '_factory_types'):
            self._factory_types = {}
        return self._factory_types

    security.declareProtected(ManagePortal, 'manage_setPortalFactoryTypes')

    def manage_setPortalFactoryTypes(self, REQUEST=None, listOfTypeIds=None):
        """Set the portal types that should use the factory."""
        if listOfTypeIds is not None:
            dict = {}
            for l in listOfTypeIds:
                dict[l] = 1
        elif REQUEST is not None:
            dict = REQUEST.form
        if dict is None:
            dict = {}
        self._factory_types = {}
        types_tool = getToolByName(self, 'portal_types')
        for t in types_tool.listContentTypes():
            if t in dict:
                self._factory_types[t] = 1
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_main')

    def doCreate(self, obj, id=None, **kw):
        """Create a real object from a temporary object."""
        if self.isTemporary(obj=obj):
            if id is not None:
                id = id.strip()
            if not id:
                if hasattr(obj, 'getId') and callable(getattr(obj, 'getId')):
                    id = obj.getId()
                else:
                    id = getattr(obj, 'id', None)
            # get the ID of the TempFolder
            type_name = aq_parent(aq_inner(obj)).id
            folder = aq_parent(aq_parent(aq_parent(aq_inner(obj))))
            folder.invokeFactory(id=id, type_name=type_name)
            obj = getattr(folder, id)

            # give ownership to currently authenticated member if not anonymous
            # TODO is this necessary?
            membership_tool = getToolByName(self, 'portal_membership')
            if not membership_tool.isAnonymousUser():
                member = membership_tool.getAuthenticatedMember()
                obj.changeOwnership(member.getUser(), 1)
            if hasattr(aq_base(obj), 'manage_afterPortalFactoryCreate'):
                obj.manage_afterPortalFactoryCreate()
        return obj

    def _fixRequest(self):
        """Our before_publishing_traverse call mangles URL0.  This fixes up
        the REQUEST."""
        # Everything seems to work without this method being called at all...
        factory_info = self.REQUEST.get(FACTORY_INFO, None)
        if not factory_info:
            return
        stack = factory_info['stack']
        FACTORY_URL = self.REQUEST.URL
        URL = '/'.join([FACTORY_URL] + stack)
        self.REQUEST.set('URL', URL)

        url_list = URL.split('/')
        n = 0
        while len(url_list) > 0 and url_list[-1] != '':
            self.REQUEST.set('URL%d' % n, '/'.join(url_list))
            url_list = url_list[:-1]
            n = n + 1

        # BASE1 is the url of the Zope App object
        n = len(self.REQUEST._steps) + 2
        base = FACTORY_URL
        for part in stack:
            base = '%s/%s' % (base, part)
            self.REQUEST.set('BASE%d' % n, base)
            n += 1
        # TODO fix URLPATHn, BASEPATHn here too

    def isTemporary(self, obj):
        """Check to see if an object is temporary"""
        ob = aq_base(aq_parent(aq_inner(obj)))
        return (hasattr(ob, 'meta_type')
                and ob.meta_type == TempFolder.meta_type)

    def __before_publishing_traverse__(self, other, REQUEST):

        if REQUEST.get(FACTORY_INFO, None):
            del REQUEST[FACTORY_INFO]

        stack = REQUEST.get('TraversalRequestNameStack')
        # convert from unicode if necessary (happens in Epoz for some weird
        # reason)
        stack = [str(s) for s in stack]

        # need 2 more things on the stack at least for portal_factory to
        # kick in:
        #    (1) a type, and (2) an id
        if len(stack) < 2:  # ignore
            return

        # Keep track of how many path elements we want to eat
        gobbled_length = 0

        type_name = stack[-1]
        types_tool = getToolByName(self, 'portal_types')
        # make sure this is really a type name
        if not type_name in types_tool.listContentTypes():
            return  # nope -- do nothing

        gobbled_length += 1

        id = stack[-2]
        intended_parent = aq_parent(self)
        if hasattr(intended_parent, id):
            return  # do normal traversal via __bobo_traverse__

        gobbled_length += 1

        # about to create an object

        # before halting traversal, check for method aliases
        # stack should be [...optional stuff..., id, type_name]
        key = len(stack) >= 3 and stack[-3] or '(Default)'
        ti = types_tool.getTypeInfo(type_name)
        method_id = ti and ti.queryMethodID(key)
        if method_id:
            if key != '(Default)':
                del(stack[-3])
            if method_id != '(Default)':
                stack.insert(-2, method_id)
                gobbled_length += 1
            REQUEST._hacked_path = 1
        else:
            gobbled_length += 1

        # Pevent further traversal if we are doing a normal factory request,
        # but allow it if there is a traversal sub-path beyond the (edit)
        # view on the content item. In this case, portal_factory will not
        # be responsible for rendering the object.
        if len(stack) <= gobbled_length:
            REQUEST.set('TraversalRequestNameStack', [])

        stack.reverse()
        factory_info = {'stack': stack}
        REQUEST.set(FACTORY_INFO, factory_info)

    def __bobo_traverse__(self, REQUEST, name):
        # __bobo_traverse__ can be invoked directly by a restricted_traverse
        # method call in which case the traversal stack will not have been
        # cleared by __before_publishing_traverse__
        name = str(name)  # fix unicode weirdness
        types_tool = getToolByName(self, 'portal_types')
        if not name in types_tool.listContentTypes():
            # not a type name -- do the standard thing
            return getattr(self, name)
        # a type name -- return a temp folder
        return self._getTempFolder(str(name))

    security.declarePublic('__call__')

    def __call__(self, *args, **kwargs):
        """call method"""
        self._fixRequest()
        factory_info = self.REQUEST.get(FACTORY_INFO, {})
        stack = factory_info['stack']
        type_name = stack[0]
        id = stack[1]

        # do a passthrough if parent contains the id
        if id in aq_parent(self):
            return (aq_parent(self)
                    .restrictedTraverse('/'.join(stack[1:]))(*args, **kwargs))

        tempFolder = self._getTempFolder(type_name)
        # Mysterious hack that fixes some problematic interactions with
        # SpeedPack:
        #   Get the first item in the stack by explicitly calling __getitem__
        temp_obj = tempFolder.__getitem__(id)
        stack = stack[2:]
        if stack:
            try:
                obj = temp_obj.restrictedTraverse('/'.join(stack))
            except AttributeError:
                raise NotFound

            # Mimic URL traversal, sort of
            if getattr(aq_base(obj), 'index_html', None):
                obj = obj.restrictedTraverse('index_html')
            else:
                obj = getattr(obj, 'GET', obj)

        else:
            obj = temp_obj
        return mapply(obj, self.REQUEST.args, self.REQUEST,
                      call_object, 1, missing_name,
                      dont_publish_class, self.REQUEST, bind=1)

    index_html = None  # call __call__, not index_html

    def _getTempFolder(self, type_name):
        factory_info = self.REQUEST.get(FACTORY_INFO, {})
        tempFolder = factory_info.get(type_name, None)
        if tempFolder is not None:
            tempFolder = aq_inner(tempFolder).__of__(self)
            return tempFolder

        # make sure we can add an object of this type to the temp folder
        types_tool = getToolByName(self, 'portal_types')
        if not type_name in types_tool.TempFolder.allowed_content_types:
            # update allowed types for tempfolder
            types_tool.TempFolder.allowed_content_types = \
                (types_tool.listContentTypes())

        tempFolder = TempFolder(type_name).__of__(self)

        factory_info[type_name] = tempFolder
        self.REQUEST.set(FACTORY_INFO, factory_info)
        return tempFolder

InitializeClass(FactoryTool)
