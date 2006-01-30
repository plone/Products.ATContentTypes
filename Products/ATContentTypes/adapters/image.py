from Products.ATContentTypes.interface.image import IPhotoAlbum
from Products.ATContentTypes.interface.dataExtractor import IDataExtractor
from Products.ATContentTypes.interface.folder import IFilterFolder
from zope.interface import implements

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

