"""AT Content Types configuration file
"""

import os

## options for mx tidy
## read http://www.egenix.com/files/python/mxTidy.html for more informations
MX_TIDY_ENABLED = True
MX_TIDY_OPTIONS= dict(
    drop_font_tags=True,
    drop_empty_paras=True,
    input_xml=False,
    output_xhtml=True,
    quiet=True,
    show_warnings=True,
    indent_spaces=True,
    word_2000=True,
    wrap=72,
    tab_size=4,
    char_encoding='utf8',
)

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


PIL_CONFIG_QUALITY = 90
PIL_CONFIG_RESIZE_ALGO = 'antialias'

ALLOW_DOCUMENT_UPLOAD = True
DEFAULT_CONTENT_TYPE = 'text/html'
MAX_FILE_SIZE = False
MAX_IMAGE_DIMENSION = (0, 0)
