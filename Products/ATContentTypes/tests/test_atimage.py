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
"""
"""

__author__ = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase

from Acquisition import aq_base

from OFS.Image import Image as OFSImage

from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.public import *
from Products.ATContentTypes.tests.utils import dcEdit
import time

from Products.ATContentTypes.content.image import ATImage
from Products.ATContentTypes.content.image import ATImageSchema
from Products.ATContentTypes.migration.atctmigrator import ImageMigrator
from Products.ATContentTypes.interfaces import IImageContent
from Products.ATContentTypes.interfaces import IATImage
from Products.CMFDefault.Image import Image
from Interface.Verify import verifyObject

_here = os.path.dirname(__file__)
TEST_GIF = open(os.path.join(_here, 'test.gif'), 'rb').read()
TEST_JPEG = open(os.path.join(_here, 'CanonEye.jpg'), 'rb').read()

def editCMF(obj):
    obj.update_data(TEST_JPEG, content_type="image/jpeg")
    dcEdit(obj)

def editATCT(obj):
    obj.setImage(TEST_JPEG, content_type="image/jpeg")
    dcEdit(obj)

tests = []

class TestSiteATImage(atcttestcase.ATCTTypeTestCase):

    klass = ATImage
    portal_type = 'Image'
    cmf_portal_type = 'CMF Image'
    cmf_klass = Image
    title = 'Image'
    meta_type = 'ATImage'
    icon = 'image_icon.gif'

    def test_implementsImageContent(self):
        iface = IImageContent
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_implementsATImage(self):
        iface = IATImage
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_dcEdit(self):
        #if not hasattr(self, '_cmf') or not hasattr(self, '_ATCT'):
        #    return
        old = self._cmf
        new = self._ATCT
        new.setImage(TEST_JPEG, content_type="image/jpeg")
        dcEdit(old)
        dcEdit(new)
        self.compareDC(old, new)

    def test_edit(self):
        old = self._cmf
        new = self._ATCT
        editCMF(old)
        editATCT(new)
        self.failUnless(old.Title() == new.Title(), 'Title mismatch: %s / %s' \
                        % (old.Title(), new.Title()))
        self.failUnless(old.Description() == new.Description(), 'Description mismatch: %s / %s' \
                        % (old.Description(), new.Description()))

    def test_migration(self):
        old = self._cmf
        id  = old.getId()

        # edit
        editCMF(old)
        title       = old.Title()
        description = old.Description()
        mod         = old.ModificationDate()
        created     = old.CreationDate()

        # migrated (needs subtransaction to work)
        get_transaction().commit(1)
        m = ImageMigrator(old)
        m(unittest=1)

        self.failUnless(id in self.folder.objectIds(), self.folder.objectIds())
        migrated = getattr(self.folder, id)

        self.compareAfterMigration(migrated, mod=mod, created=created)
        self.compareDC(migrated, title=title, description=description)

    def test_getEXIF(self):
        # NOTE: not a real test
        exif_data = self._ATCT.getEXIF()
        self.failUnless(isinstance(exif_data, dict), type(exif_data))
        
    def test_exifOrientation(self):
        # NOTE: not a real test
        r, m = self._ATCT.getEXIFOrientation()
        
    def test_transform(self):
        # NOTE: not a real test
        self._ATCT.transformImage(2)

    def test_autotransform(self):
        # NOTE: not a real test
        self._ATCT.autoTransformImage()
        
    def test_broken_pil(self):
        # PIL has a nasty bug when the image ratio is too extrem like 300x15:
        # Module PIL.Image, line 1136, in save
        # Module PIL.PngImagePlugin, line 510, in _save
        # Module PIL.ImageFile, line 474, in _save
        # SystemError: tile cannot extend outside image
        atct = self._ATCT
        
        # test upload
        atct.setImage(TEST_GIF, mimetype='image/gif', filename='test.gif')
        self.failUnlessEqual(atct.getImage().data, TEST_GIF)
        
    def test_bobo_hook(self):
        atct = self._ATCT
        REQUEST = {'method' : 'GET'}
        scales = atct.getField('image').getAvailableSizes(atct)
        atct.setImage(TEST_GIF, mimetype='image/gif', filename='test.gif')
        
        img = atct.__bobo_traverse__(REQUEST, 'image')
        self.failUnless(isinstance(img, OFSImage), img)
        
        # test if all scales exist
        for scale in scales.keys():
            name = 'image_' + scale
            img = atct.__bobo_traverse__(REQUEST, name)
            self.failUnless(isinstance(img, OFSImage), img)

    def test_division_by_0_pil(self):
        # pil generates a division by zero error on some images
        atct = self._ATCT
        
        # test upload
        TEST2_GIF = open(os.path.join(_here, 'test_DivisionError.jpg'), 'rb').read()
        atct.setImage(TEST2_GIF, mimetype='image/gif', filename='test_DivisionError.jpg')
        self.failUnlessEqual(atct.getImage().data, TEST2_GIF)
        
tests.append(TestSiteATImage)

class TestATImageFields(atcttestcase.ATCTFieldTestCase):


    def afterSetUp(self):
        atcttestcase.ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATImage)

    def test_imageField(self):
        dummy = self._dummy
        field = dummy.getField('image')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 1, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 0, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getImage',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setImage',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == CMFCorePermissions.View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        CMFCorePermissions.ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'image', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AnnotationStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AnnotationStorage(migrate=True),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == "(('isNonEmptyFile', V_REQUIRED), ('checkImageMaxSize', V_REQUIRED))",
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, ImageWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))
        self.failUnless(field.primary == 1, 'Value is %s' % field.primary)


tests.append(TestATImageFields)

from Products.ATContentTypes.lib import exif
TEST_CANONEYE_JPG = open(os.path.join(_here, 'CanonEye.jpg'), 'rb').read()
class TestSiteATImageExif(atcttestcase.ATCTTypeTestCase):

    klass = ATImage
    portal_type = 'Image'
    cmf_portal_type = 'CMF Image'
    cmf_klass = Image
    title = 'Image'
    meta_type = 'ATImage'
    icon = 'image_icon.gif'

    def test_broken_exif(self):

        #EXIF data in images from Canon digicams breaks EXIF of 2005.05.12 with following exception
        # 
      	#2005-05-01T19:21:16 ERROR(200) Archetypes None
        #Traceback (most recent call last):
        #  File "/home/russ/cb/var/zope/Products/ATContentTypes/content/image.py", line 207, in getEXIF
        #    exif_data = exif.process_file(img, debug=False, noclose=True)
        #  File "/home/russ/cb/var/zope/Products/ATContentTypes/lib/exif.py", line 1013, in process_file
        #    hdr.decode_maker_note()
        #  File "/home/russ/cb/var/zope/Products/ATContentTypes/lib/exif.py", line 919, in decode_maker_note
        #    dict=MAKERNOTE_CANON_TAGS)
        #  File "/home/russ/cb/var/zope/Products/ATContentTypes/lib/exif.py", line 753, in dump_IFD
        #    raise ValueError, \
        #ValueError: unknown type 768 in tag 0x0100
        #

        # This test fails even with the 2005.05.12 exif version from 
        #    http://home.cfl.rr.com/genecash/

        atct = self._ATCT
        atct.setImage(TEST_CANONEYE_JPG, mimetype='image/jpeg', filename='CanonImage.jpg')
        canonImage = atct.getImageAsFile(scale=None)
        exif_data = exif.process_file(canonImage, debug=False)        
        # probably want to add some tests on returned data. Currently gives 
        #  ValueError in process_file 

tests.append(TestSiteATImageExif)

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        for test in tests:
            suite.addTest(unittest.makeSuite(test))
        return suite
