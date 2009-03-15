import logging
from cStringIO import StringIO

from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo
from ExtensionClass import Base
from DateTime import DateTime
from App.class_init import InitializeClass
from OFS.Image import Image as OFSImage
from OFS.Image import Pdata

# third party extension
import exif

LOG = logging.getLogger('ATCT.image')


class ATCTImageTransform(Base):
    """Base class for images containing exif functions.
    """

    security = ClassSecurityInfo()

    security.declarePrivate('getImageAsFile')
    def getImageAsFile(self, img=None, scale=None):
        """Get the img as file like object
        """
        if img is None:
            f = self.getField('image')
            img = f.getScale(self, scale)
        # img.data contains the image as string or Pdata chain
        data = None
        if isinstance(img, OFSImage):
            data = str(img.data)
        elif isinstance(img, Pdata):
            data = str(img)
        elif isinstance(img, str):
            data = img
        elif isinstance(img, file) or (hasattr(img, 'read') and
          hasattr(img, 'seek')):
            img.seek(0)
            return img
        if data:
            return StringIO(data)
        else:
            return None

    # image related code like exif and rotation
    # partly based on CMFPhoto

    security.declareProtected(View, 'getEXIF')
    def getEXIF(self, img=None, refresh=False):
        """Get the exif informations of the file

        The information is cached in _v_image_exif
        """
        cache = '_image_exif'

        if refresh:
            setattr(self, cache, None)

        exif_data = getattr(self, cache, None)

        if exif_data is None or not isinstance(exif_data, dict):
            io = self.getImageAsFile(img, scale=None)
            if io is not None:
                # some cameras are naughty :(
                try:
                    io.seek(0)
                    exif_data = exif.process_file(io, debug=False)
                except:
                    LOG.error('Failed to process EXIF information', exc_info=True)
                    exif_data = {}
                # seek to 0 and do NOT close because we might work
                # on a file upload which is required later
                io.seek(0)
                # remove some unwanted elements lik thumb nails
                for key in ('JPEGThumbnail', 'TIFFThumbnail',
                            'MakerNote JPEGThumbnail'):
                    if key in exif_data:
                        del exif_data[key]

        if not exif_data:
            # alawys return a dict
            exif_data = {}
        # set the EXIF cache even if the image has returned an empty
        # dict. This prevents regenerating the exif every time if an
        # image doesn't have exif information.
        setattr(self, cache, exif_data)
        return exif_data

    security.declareProtected(View, 'getEXIFOrientation')
    def getEXIFOrientation(self):
        """Get the rotation and mirror orientation from the EXIF data

        Some cameras are storing the informations about rotation and mirror in
        the exif data. It can be used for autorotation.
        """
        exif = self.getEXIF()
        mirror = 0
        rotation = 0
        code = exif.get('Image Orientation', None)

        if code is None:
            return (mirror, rotation)

        try:
            code = int(code)
        except ValueError:
            return (mirror, rotation)

        if code in (2, 4, 5, 7):
            mirror = 1
        if code in (1, 2):
            rotation = 0
        elif code in (3, 4):
            rotation = 180
        elif code in (5, 6):
            rotation = 90
        elif code in (7, 8):
            rotation = 270

        return (mirror, rotation)

    security.declareProtected(View, 'getEXIFOrigDate')
    def getEXIFOrigDate(self):
        """Get the EXIF DateTimeOriginal from the image (or None)
        """
        exif_data = self.getEXIF()
        raw_date = exif_data.get('EXIF DateTimeOriginal', None)
        if raw_date is not None:
            # some cameras are naughty ...
            try:
                return DateTime(str(raw_date))
            except:
                LOG.error('Failed to parse exif date %s' % raw_date, exc_info=True)
        return None

InitializeClass(ATCTImageTransform)
