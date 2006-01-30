from Products.ATContentTypes.z3.interfaces import IPhotoAlbum
from zope.interface import implements
from interfaces import IArchiveAccumulator
from interfaces import IFilterFolder
from interfaces import IArchiver
from interfaces import IDataExtractor
from interfaces import IArchivable
from cStringIO import StringIO
from zipfile import ZipFile

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

class FolderishArchiver(object):
    """
    store your files in a zip file
    """
    implements(IArchiver)
#XXXX Refactor so that init and getRawZip methods inside Folderish and non Folderish object
    def __init__(self, context):
        """
        """
        self.context = context

    def getRawArchive(self, accumulator=None, **kwargs):
        """
        """
        if(not accumulator):
            accumulator = ZipAccumulator(self.context)
        self.getArchive(None,accumulator, **kwargs)
        return accumulator.getRaw()

    def getArchive(self, path, accumulator, **kwargs):
        """
        get the archive file object
        """
        recursive = kwargs.get('recursive',0)
#        if(IArchiveAccumulator.providedBy(accumulator)):
#            raise ValueError, "accumulator must implement IArchiveAccumulaotor"
        adapter = IFilterFolder(self.context)
        for item in adapter.listObjects():
            if IArchivable.providedBy(item):
                archiver = IArchiver(item)
                folderish = isinstance(archiver,FolderishArchiver)
                if (recursive and folderish and path):
                    path = '%s/%s' % (path, self.context.getId())
                    archiver.getArchive(path, accumulator, **kwargs)
                if not folderish:
                    path = self.context.getId()
                    archiver.getArchive(path, accumulator, **kwargs)

class DocumentDataExtractor(object):
    """
    """
    def __init__(self, context):
        self.context = context

    def getData(self,**kwargs):
        """
        """
        return self.context.CookedBody()

class NonFolderishArchiver(object):
    """
    store your files in a zip file
    """
    implements(IArchiver)
    def __init__(self, context):
        self.context = context

    def getRawArchive(self, accumulator=None, **kwargs):
        if(not accumulator):
            accumulator = IZipAccumulator(self.context)
        self.getArchive(accumulator, **kwargs)
        return self.accumulator.getRawZip()

    def getArchive(self, path, accumulator, **kwargs):
        """
        get the zip file object
        """
#        if(IArchiveAccumulator.providedBy(accumulator)):
#            raise ValueError, "accumulator must implement IArchiveAccumulaotor"
        dataExtractor = IDataExtractor(self.context)
        if dataExtractor and IArchivable.providedBy(self.context):
            data = dataExtractor.getData(**kwargs)
            filepath = '%s/%s' % (path, self.context.getId())
            accumulator.setFile(filepath,data)

class PhotoAlbumFilter(object):
    """
    """
    implements(IFilterFolder)

    def __init__(self, context):
        self.context = context

    def listObjects(self):
        return [item for item in self.context.ObjectValues(['Image','PhotoAlbum'])]


class FolderFilter(object):
    """
    """
    implements(IFilterFolder)

    def __init__(self, context):
        self.context = context

    def listObjects(self):
        return self.context.objectValues()

class ZipAccumulator(object):
    """
    """
    implements(IArchiveAccumulator)

    _zip = None
    sIO = None

    def __init__(self, context):
        self.context = context
        self.initIO()

    def initIO(self):
        """
        reinit the Zip IO
        """
        self.sIO = StringIO()
        self._zip = ZipFile(self.sIO,"w",8)

    def setFile(self,filename,data):
        """
        store the file inside the zip file
        """
        if(self._zip):
            self._zip.writestr(filename,data)
        else:
            raise BadRequest,"Unitialized Zip file"

    def setZip(self):
        """
        initialize the zipe file
        """
        self._zip = ZipFile(self.sIO,"w",8)

    def close(self):
        """
        close the zip file
        """
        self._zip.close()

    def getRaw(self):
        """
        return the raw zip file
        """
        if(self._zip):
            self.close()
            value = self.sIO.getvalue()
            self.setZip()
            return value
        else:
            raise BadRequest,"Unitialized Zip file"


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

