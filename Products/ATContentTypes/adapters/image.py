from Products.ATContentTypes.z3.interfaces import IPhotoAlbum
from zope.interface import implements
from interfaces import IArchiveAccumulator
from interfaces import IFilterFolder
from interfaces import IArchiver
from interfaces import IDataExtractor
from interfaces import IArchivable
from cStringIO import StringIO
from zipfile import ZipFile
from Acquisition import aq_parent

class PhotoDataExtractor(object):
    """
    """
    implements(IDataExtractor)
    def __init__(self, context):
        self.context = context

    def getData(self, format=None,width=None,height=None,**kwargs):
        if format:
### changeFormat
            pass
        if width or height:
### changeSize
            pass
        return data

class PhotoAlbumFilter(object):
    """
    """
    implements(IFilterFolder)

    def __init__(self, context):
        self.context = context

    def listObjects(self):
        return [item for item in self.context.ObjectValues(['Image','PhotoAlbum'])]

class PhotoAlbum(object):
    """
    interface that adapts a folder into a photo album
    """

    implements(IPhotoAlbum)
    def __init__(self, context):
        self.context = context

    def setSymbolicPhoto(self,photo=None):
        """
        set the photo which represents the album
        """
        pass


    def getSymbolicPhoto():
        """
        get the photo which represents the album
        """
        pass

