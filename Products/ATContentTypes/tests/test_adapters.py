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

from Products.Archetypes.public import *

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.interfaces import IATFolder
from Products.Five.traversable import FakeRequest
from Products.ATContentTypes.tests.utils import FakeRequestSession

from Products.ATContentTypes.z3.interfaces import IPhotoAlbum
from Products.ATContentTypes.z3.interfaces import IArchiver
from Products.ATContentTypes.z3.interfaces import IArchivable
from Products.ATContentTypes.z3.interfaces import IPhotoAlbumAble

from Products.ATContentTypes.z3.adapters import PhotoAlbum
from Products.ATContentTypes.z3.adapters import FolderishArchiver

from Products.ATContentTypes.z3.browser import ArchiveView

from zope.interface.verify import verifyClass
from zipfile import ZipFile
from cStringIO import StringIO

tests = []


class TestSitePhotoAlbumSupport(atcttestcase.ATCTSiteTestCase):
    def afterSetUp(self):
        atcttestcase.ATCTSiteTestCase.afterSetUp(self)
        self.folder.invokeFactory('Folder', 'fobj', title='folder 1')
        self.fobj = self.folder.fobj

    def test_implements(self):
        self.failUnless(IPhotoAlbumAble.providedBy(self.fobj))

    def test_adapter(self):
        verifyClass(IPhotoAlbum,PhotoAlbum)

    def test_SymbolicPhoto(self):
        adapted = IPhotoAlbum(self.fobj)

class TestFolderishArchiver(atcttestcase.ATCTSiteTestCase):
    def afterSetUp(self):
        atcttestcase.ATCTSiteTestCase.afterSetUp(self)
        self.folder.invokeFactory('Folder', 'fobj', title='folder 1')
        self.fobj = self.folder.fobj
        self.fobj.invokeFactory('Document','doc1',title='document 1')
        self.fobj.doc1.setText("A nice text")

    def test_implements(self):
        archiver = IArchiver(self.fobj)
        self.failUnless(IArchiver.providedBy(archiver))

    def test_adapter(self):
        verifyClass(IArchiver,FolderishArchiver)

    def test_getArchive(self):
### FOLDERISH
        archiver = IArchiver(self.fobj)
        zipFile = archiver.getRawArchive()
        zip = ZipFile(StringIO(zipFile),"r",8)
        self.assertEqual(zip.namelist(),['fobj/doc1'])
        self.assertEqual(zip.read('fobj/doc1'),"A nice text")
### NON Folderish
        archiver = IArchiver(self.fobj.doc1)
        zipFile = archiver.getRawArchive()
        zip = ZipFile(StringIO(zipFile),"r",8)
        self.assertEqual(zip.namelist(),['fobj/doc1'])


#tests.append(TestAutoSortSupport)


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
