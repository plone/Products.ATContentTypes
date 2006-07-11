import logging
from cStringIO import StringIO

from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
import AccessControl.Owned
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.permissions import View

from Products.ATContentTypes.interfaces import IImageContent
from Products.ATContentTypes.interfaces import IATCTTool
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.config import ATCT_DIR
from Products.ATContentTypes.config import WWW_DIR
from Products.ATContentTypes.tool.topic import ATTopicsTool

LOG = logging.getLogger('ATCT')

def log(message,summary='',severity=0):
    LOG.log(severity, 'ATCT: %s \n%s', summary, message)

class ATCTTool(UniqueObject, SimpleItem, PropertyManager, ATTopicsTool):
    """ATContentTypes tool
    """
    security = ClassSecurityInfo()

    id = TOOLNAME
    meta_type= 'ATCT Tool'
    title = 'ATContentTypes Tool'

    __implements__ = (SimpleItem.__implements__, IATCTTool,
                      ATTopicsTool.__implements__)

    manage_options =  (
            {'label' : 'Overview', 'action' : 'manage_overview'},
            {'label' : 'Image scales', 'action' : 'manage_imageScales'}
        ) + PropertyManager.manage_options + \
            AccessControl.Owned.Owned.manage_options

    # properties and their default values

    _properties = PropertyManager._properties + (
        {'id' : 'image_types', 'type' : 'multiple selection',
         'mode' : 'w', 'select_variable' : 'listContentTypes'},
        {'id' : 'folder_types', 'type' : 'multiple selection',
         'mode' : 'w', 'select_variable' : 'listContentTypes'},
        {'id' : 'album_batch_size', 'type' : 'int', 'mode' : 'w'},
        {'id' : 'album_image_scale', 'type' : 'string', 'mode' : 'w'},
        {'id' : 'single_image_scale', 'type' : 'string', 'mode' : 'w'},
        )

    # list of portal types with an Image field used for rescale
    # and album listing
    image_types = ('Image', 'News Item',)
    # list of portal types to display as album folder
    folder_types = ('Folder', 'Large Plone Folder')
    # album batch size
    album_batch_size = 30
    # scale name for image in batch view
    album_image_scale = 'thumb'
    # scale name for image in single view
    single_image_scale = 'preview'

    # templates

    security.declareProtected(ManagePortal, 'manage_imageScales')
    manage_imageScales = PageTemplateFile('imageScales', WWW_DIR)

    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('overview', WWW_DIR)

    def om_icons(self):
        icons = ({
                    'path':'misc_/ATContentTypes/tool.gif',
                    'alt':self.meta_type,
                    'title':self.meta_type,
                 },)
        return icons

    # image scales

    security.declareProtected(ManagePortal, 'recreateImageScales')
    def recreateImageScales(self, portal_type=None):
        """Recreates AT Image scales (doesn't remove unused!)
        """
        if portal_type is None:
            portal_type = tuple(self.image_types)
        out = StringIO()
        print >> out, "Updating AT Image scales"
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog(portal_type = portal_type,
                         portal_type_operator = 'or')
        for brain in brains:
            obj = brain.getObject()
            if obj is None:
                continue

            if not IImageContent.isImplementedBy(obj):
                continue

            try: state = obj._p_changed
            except: state = 0

            field = obj.getField('image')
            if field is not None:
                print >>out, 'Updating %s' % obj.absolute_url(1)
                field.removeScales(obj)
                field.createScales(obj)

            if state is None: obj._p_deactivate()

        print >> out, "Updated AT Image scales"
        return out.getvalue()

    security.declareProtected(ManagePortal, 'listContentTypes')
    def listContentTypes(self):
        """List all available content types

        Used for properties
        """
        ttool = getToolByName(self, 'portal_types')
        return ttool.listContentTypes()

InitializeClass(ATCTTool)
