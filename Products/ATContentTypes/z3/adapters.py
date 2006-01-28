from Products.ATContentTypes.z3.interfaces import IPhotoAlbum
from zope.interface import implements

class PhotoAlbum(object):
    """
    interface that adapts a folder into a photo album
    """

    implements(IPhotoAlbum)
    def __init__(self, context):
        self.context = context

    def setSymbolicPhoto(photo=None):
        """
        set the photo which represents the album
        """
        pass


    def getSymbolicPhoto():
        """
        get the photo which represents the album
        """
        pass

