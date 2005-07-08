#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2005 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""Image transformation code

The basics for the EXIF information, orientation code and the rotation code
were taken from CMFPhoto.
"""
__author__  = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'

from cStringIO import StringIO

from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from ExtensionClass import Base
from DateTime import DateTime
from Globals import InitializeClass

from Products.ATContentTypes.lib import exif
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.config import HAS_PIL
from Products.Archetypes.public import log_exc

from OFS.Image import Image as OFSImage

# the following code is based on the rotation code of Photo
if HAS_PIL:
    import PIL.Image


# transpose constants, taken from PIL.Image to maintain compatibilty
FLIP_LEFT_RIGHT = 0
FLIP_TOP_BOTTOM = 1
ROTATE_90 = 2
ROTATE_180 = 3
ROTATE_270 = 4


TRANSPOSE_MAP = {
    FLIP_LEFT_RIGHT : "Flip around vertical axis",
    FLIP_TOP_BOTTOM : "Flip around horizontal axis",
    ROTATE_270      : "Rotate 90 clockwise",
    ROTATE_180      : "Rotate 180",
    ROTATE_90       : "Rotate 90 counterclockwise",
   }
   
AUTO_ROTATE_MAP = {
    0   : None,
    90  : ROTATE_270,
    180 : ROTATE_180,
    270 : ROTATE_90,
    }



class ATCTImageTransform(Base):
    """Base class for images containing transformation and exif functions
    
    * exif information
    * image rotation
    """
    
    actions = (
        {
        'id'          : 'transform',
        'name'        : 'Transform',
        'action'      : 'string:${object_url}/atct_image_transform',
        'permissions' : (CMFCorePermissions.ModifyPortalContent,),
        'condition'   : 'object/hasPIL',
         },
        )
    
    security = ClassSecurityInfo()

    security.declarePrivate('getImageAsFile')
    def getImageAsFile(self, scale=None):
        """Get the img as file like object
        """
        f = self.getField('image')
        img = f.getScale(self, scale)
        # img.data contains the image as string or Pdata chain
        # TODO: explicit check for Pdata or file handler
        if isinstance(img, OFSImage):
            data = str(img.data)
        else:
            data = str(img)
        if data:
            return StringIO(data)
        else:
            return None

    # image related code like exif and rotation
    # partly based on CMFPhoto
    
    security.declareProtected(CMFCorePermissions.View, 'getEXIF')
    def getEXIF(self, refresh=False):
        """Get the exif informations of the file
        
        The information is cached in _v_image_exif
        """
        cache = '_image_exif'
        
        if refresh:
            setattr(self, cache, None)
        
        exif_data = getattr(self, cache, None)
        
        if exif_data is None or not isinstance(exif_data, dict):
            img = self.getImageAsFile(scale=None)
            if img:
                # some cameras are naughty :(
                try:
                    img.seek(0)
                    exif_data = exif.process_file(img, debug=False)
                    img.close()
                except:
                    log_exc()
                    exif_data = {}
                # remove some unwanted elements lik thumb nails
                for key in ('JPEGThumbnail', 'TIFFThumbnail'):
                    if key in exif_data:
                        del exif_data[key]

        if not exif_data:
            # alawys return a dict
            exif_data = {}
        else:
            setattr(self, cache, exif_data)
        return exif_data

    security.declareProtected(CMFCorePermissions.View, 'getEXIFOrientation')
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
    
    def getEXIFOrigDate(self):
        """Get the EXIF DateTimeOriginal from the image (or None)
        """
        exif_data = self.getEXIF()
        # some cameras are naughty ...
        try:
            raw_date = exif_data.get('EXIF DateTimeOriginal', None)
            if raw_date is not None:
                return DateTime(str(raw_date))
        except:
            log_exc()
            return None

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 
                              'transformImage')
    def transformImage(self, method, REQUEST=None):
        """
        Transform an Image:
            FLIP_LEFT_RIGHT
            FLIP_TOP_BOTTOM
            ROTATE_90 (rotate counterclockwise)
            ROTATE_180
            ROTATE_270 (rotate clockwise)
        """ 
        method = int(method)
        if method not in TRANSPOSE_MAP:
            raise RuntimeError, "Unknown method %s" % method
        
        target = self.absolute_url() + '/atct_image_transform'
        
        if not HAS_PIL:
            if REQUEST:
                REQUEST.RESPONSE.redirect(target)
        
        image = self.getImageAsFile()
        image2 = StringIO()
        
        if image:
            img = PIL.Image.open(image)
            del image
            fmt = img.format
            img = img.transpose(method)
            img.save(image2, fmt, quality=zconf.pil_config.quality)
            
            field = self.getField('image')
            mimetype = field.getContentType(self)
            filename = field.getFilename(self)
            
            # because AT tries to get mimetype and filename from a file like
            # object by attribute access I'm passing a string along
            self.setImage(image2.getvalue(), mimetype=mimetype,
                          filename=filename, refresh_exif=False)
        
        if REQUEST:
             REQUEST.RESPONSE.redirect(target)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 
                              'autoTransformImage')
    def autoTransformImage(self, REQUEST=None):
        """Auto transform image according to EXIF data
        
        Note: isn't using mirror
        """
        target = self.absolute_url() + '/atct_image_transform'
        mirror, rotation = self.getEXIFOrientation()
        if rotation:
            transform = AUTO_ROTATE_MAP.get(rotation)
            if transform:
                self.transformImage(transform)
        if REQUEST:
             REQUEST.RESPONSE.redirect(target)
             
    security.declareProtected(CMFCorePermissions.View, 'getTransformMap')
    def getTransformMap(self):
        """Get map for tranforming the image
        """
        return [{'name' : n, 'value' : v} for v, n in TRANSPOSE_MAP.items()]
    
    security.declareProtected(CMFCorePermissions.View, 'hasPIL')
    def hasPIL(self):
        """Is PIL installed?
        """
        return HAS_PIL

InitializeClass(ATCTImageTransform)
