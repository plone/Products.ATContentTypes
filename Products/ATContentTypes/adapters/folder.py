from Products.ATContentTypes.z3.interfaces import IPhotoAlbum
from zope.interface import implements
from Products.ATContentTypes.interfaces import IFilterFolder
from cStringIO import StringIO
from zipfile import ZipFile
from Acquisition import aq_parent

class FolderFilter(object):
    """
    """
    implements(IFilterFolder)

    def __init__(self, context):
        self.context = context

    def listObjects(self):
        return self.context.objectValues()

