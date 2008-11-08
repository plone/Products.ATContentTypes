"""AT Content Types configuration file
"""

import string
import os
from Products.ATContentTypes.configuration import zconf

## options for mx tidy
## read http://www.egenix.com/files/python/mxTidy.html for more informations
MX_TIDY_ENABLED = zconf.mxtidy.enable
MX_TIDY_OPTIONS= zconf.mxtidy.options

PROJECTNAME = "ATContentTypes"
TOOLNAME = "portal_atct"
SKINS_DIR = 'skins'

ATCT_DIR = os.path.abspath(os.path.dirname(__file__))
WWW_DIR = os.path.join(ATCT_DIR, 'www')

GLOBALS = globals()

## swallow PIL exceptions when resizing the image?
SWALLOW_IMAGE_RESIZE_EXCEPTIONS = True

## mxTidy available?
try:
    from mx import Tidy
except ImportError:
    HAS_MX_TIDY = False
else:
    HAS_MX_TIDY = True
    try:
        del Tidy
    except AttributeError:
        pass

## tidy only these document types
MX_TIDY_MIMETYPES = (
    'text/html',
     )

## LinguaPlone addon?
try:
    from Products.LinguaPlone.public import registerType
except ImportError:
    HAS_LINGUA_PLONE = False
else:
    HAS_LINGUA_PLONE = True
    del registerType

try:
    from PIL import Image
except ImportError:
    HAS_PIL = False
else:
    HAS_PIL = True

## icon map used for overwriting ATFile icons
ICONMAP = {'application/pdf' : 'pdf_icon.gif',
           'image'           : 'image_icon.gif'}

MIME_ALIAS = {
    'plain' : 'text/plain',
    'stx'   : 'text/structured',
    'html'  : 'text/html',
    'rest'  : 'text/x-rst',
    'text/stx' : 'text/structured',
    'structured-text' : 'text/structured',
    'restructuredtext' : 'text/x-rst',
    'text/restructured' : 'text/x-rst',
    }
