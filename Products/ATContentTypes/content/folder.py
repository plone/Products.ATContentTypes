from zope.interface import implements

from AccessControl import ClassSecurityInfo
from OFS.interfaces import IOrderedContainer

from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import ATCTOrderedFolder
from Products.ATContentTypes.content.base import ATCTBTreeFolder
from Products.ATContentTypes.interfaces import IATFolder as z2IATFolder
from Products.ATContentTypes.interfaces import IATBTreeFolder as z2IATBTreeFolder
from Products.ATContentTypes.interface import IATFolder
from Products.ATContentTypes.interface import IATBTreeFolder
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import NextPreviousAwareSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema

from Products.ATContentTypes import ATCTMessageFactory as _

from Products.CMFCore.permissions import View

ATFolderSchema      = ATContentTypeSchema.copy() + ConstrainTypesMixinSchema + NextPreviousAwareSchema
ATBTreeFolderSchema = ATContentTypeSchema.copy() + ConstrainTypesMixinSchema

finalizeATCTSchema(ATFolderSchema, folderish=True, moveDiscussion=False)
finalizeATCTSchema(ATBTreeFolderSchema, folderish=True, moveDiscussion=False)


class ATFolder(ATCTOrderedFolder):
    """A folder which can contain other items."""

    schema         =  ATFolderSchema

    portal_type    = 'Folder'
    archetype_name = 'Folder'
    _atct_newTypeFor = {'portal_type' : 'CMF Folder', 'meta_type' : 'Plone Folder'}
    assocMimetypes = ()
    assocFileExt   = ()
    cmf_edit_kws   = ()

    implements(IATFolder, IOrderedContainer)

    # Enable marshalling via WebDAV/FTP.
    __dav_marshall__ = True

    security       = ClassSecurityInfo()

    security.declareProtected(View, 'getNextPreviousParentValue')
    def getNextPreviousParentValue(self):
        """If the parent node is also an IATFolder and has next/previous
        navigation enabled, then let this folder have it enabled by
        default as well.
        """
        parent = self.getParentNode()
        if IATFolder.providedBy(parent):
            return parent.getNextPreviousEnabled()
        else:
            return False

    def manage_afterAdd(self, item, container):
        ATCTOrderedFolder.manage_afterAdd(self, item, container)


registerATCT(ATFolder, PROJECTNAME)

class ATBTreeFolder(ATCTBTreeFolder):
    """A folder suitable for holding a very large number of items"""
    schema         =  ATBTreeFolderSchema


    portal_type    = 'Large Plone Folder'
    archetype_name = 'Large Folder'
    _atct_newTypeFor = {'portal_type' : 'CMF Large Plone Folder',
                        'meta_type' : 'Large Plone Folder'}
    assocMimetypes = ()
    assocFileExt   = ()
    cmf_edit_kws   = ()

    implements(IATBTreeFolder)

    # Enable marshalling via WebDAV/FTP.
    __dav_marshall__ = True

    security       = ClassSecurityInfo()

registerATCT(ATBTreeFolder, PROJECTNAME)
