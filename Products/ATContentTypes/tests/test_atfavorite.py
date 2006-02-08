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

from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.public import *
from Products.Archetypes.tests.atsitetestcase import portal_name

from Products.ATContentTypes.content.favorite import ATFavorite
from Products.ATContentTypes.migration.atctmigrator import FavoriteMigrator
from Products.ATContentTypes.interfaces import IATFavorite
from Products.CMFDefault.Favorite import Favorite
from Interface.Verify import verifyObject
from Products.CMFPlone import transaction

# z3 imports
from Products.ATContentTypes.interface import IATFavorite as Z3IATFavorite
from zope.interface.verify import verifyObject as Z3verifyObject

URL='/%s/Members' % portal_name

def editCMF(obj):
    obj.setTitle('Test Title')
    obj.setDescription('Test description')
    obj.edit(remote_url=URL)
    assert obj.remote_url == 'Members'
    return obj

def editATCT(obj):
    obj.setTitle('Test Title')
    obj.setDescription('Test description')
    obj.setRemoteUrl(URL)
    return obj

tests = []

class TestSiteATFavorite(atcttestcase.ATCTTypeTestCase):

    klass = ATFavorite
    portal_type = 'Favorite'
    cmf_portal_type = 'CMF Favorite'
    cmf_klass = Favorite
    title = 'Favorite'
    meta_type = 'ATFavorite'
    icon = 'favorite_icon.gif'
    def test_implementsZ3ATFavorite(self):
        iface = Z3IATFavorite
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_implementsATFavorite(self):
        iface = IATFavorite
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def XXX_DISABLED_test_edit(self):
        old = editCMF(self._cmf)
        new = editATCT(self._ATCT)
        transaction.savepoint()
        
        # CMF uid handling test ... had some issues with it
        obj = self.portal.unrestrictedTraverse(URL)
        handler = getToolByName(self.portal, 'portal_uidhandler')
        uid = old.remote_uid
        self.failUnlessEqual(handler.queryObject(uid).getPhysicalPath(), 
                             obj.getPhysicalPath())
        
        self.failUnlessEqual(old.Title(), new.Title())
        self.failUnlessEqual(old.Description(), new.Description())
        
        url = 'http://nohost%s' % URL
        self.failUnlessEqual(url, obj.absolute_url())
        
        self.failUnlessEqual(old.remote_url, URL[len(portal_name)+2:])
        self.failUnlessEqual(old.remote_url, new.remote_url)
        self.failUnlessEqual(old.getRemoteUrl(), url)
        self.failUnlessEqual(new.getRemoteUrl(), url)
        self.failUnlessEqual(old.getRemoteUrl(), new.getRemoteUrl())

    def testLink(self):
        obj = self._ATCT
        for url in ('', '/test/',):
            obj.setRemoteUrl(url)
            u = self.portal.portal_url()
            if url.startswith('/'):
                url = url[1:]
            if url:
                u='%s/%s' % (u, url)
            self.failUnlessEqual(obj.getRemoteUrl(), u)

    def XXX_DISABLED_test_migration(self):
        old = self._cmf
        id  = old.getId()

        # edit
        editCMF(old)
        title       = old.Title()
        description = old.Description()
        mod         = old.ModificationDate()
        created     = old.CreationDate()
        url         = old.getRemoteUrl()


        # migrated (needs subtransaction to work)
        transaction.commit(1)
        m = FavoriteMigrator(old)
        m(unittest=1)

        self.failUnless(id in self.folder.objectIds(), self.folder.objectIds())
        migrated = getattr(self.folder, id)

        self.compareAfterMigration(migrated, mod=mod, created=created)
        self.compareDC(migrated, title=title, description=description)

        # XXX more

        self.failUnless(migrated.getRemoteUrl() == url, 'URL mismatch: %s / %s' \
                        % (migrated.getRemoteUrl(), url))

    def test_get_size(self):
        atct = self._ATCT
        editATCT(atct)
        # url is /plone/Members but the favorite stores the url relative to
        # the portal so substract length of the portal + 2 for the two slashes
        url_len = len(URL) - len(portal_name) - 2
        self.failUnlessEqual(atct.get_size(), url_len)

tests.append(TestSiteATFavorite)

class TestATFavoriteFields(atcttestcase.ATCTFieldTestCase):

    def afterSetUp(self):
        atcttestcase.ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATFavorite)

    def test_remoteUrlField(self):
        dummy = self._dummy
        field = dummy.getField('remoteUrl')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 1, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == '_getRemoteUrl',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setRemoteUrl',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'string', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == (),
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))
        self.failUnless(field.primary == 1, 'Value is %s' % field.primary)

tests.append(TestATFavoriteFields)

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
