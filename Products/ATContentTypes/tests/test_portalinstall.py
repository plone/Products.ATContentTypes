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

__author__ = 'Whit Morriss'
__docformat__ = 'restructuredtext'


import os, sys, traceback
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from StringIO import StringIO
from AccessControl.User import UnrestrictedUser
from AccessControl.SecurityManagement import newSecurityManager
from Products.PloneTestCase import setup as ptcsetup

tests = []

class ATCTPolicyTestCase(ZopeTestCase.ZopeTestCase):
    
    def fail_tb(self, msg):
        """ special fail for capturing errors::good for integration testing(qi, etc) """
        out = StringIO()
        t, e, tb = sys.exc_info()
        traceback.print_exc(tb, out)
        self.fail("%s ::\n %s\n %s\n %s\n" %( msg, t, e,  out.getvalue()) )

class TestPortalInstallation(ATCTPolicyTestCase):
    
    def afterSetUp(self):
        self.setRoles(['Manager', 'Owner'])
        self.login()

    if ptcsetup.PLONE21:
        def test_21Install(self):
            try:
                self.folder.manage_addProduct['CMFPlone'].manage_addSite('p2')
            except :
                self.fail_tb(" Error in 2.1 Install")
    else:
        def test_ATCTCustomizationPolicy(self):
            try:
                self.app.manage_addProduct['CMFPlone'].manage_addSite('p2', custom_policy='ATContentTypes Site')
            except :
                self.fail_tb(" Error in ATCT Customization Policy")

tests.append(TestPortalInstallation)

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
