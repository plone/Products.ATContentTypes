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

__author__ = 'Martin Aspeli <optilude@gmx.net>'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.interfaces import IATCTTool
from Interface.Verify import verifyObject

from Products.Archetypes.public import Schema, IntegerField

from Products.ATContentTypes.utils import moveFieldInSchema


tests = []

class TestMoveFieldInSchema(atcttestcase.ATCTSiteTestCase):

    def afterSetUp(self):
        self.schema = Schema((
                        IntegerField('field1'),
                        IntegerField('field2'),
                        IntegerField('field3'),
                        IntegerField('field4', schemata = 'alt'),
                        IntegerField('field5', schemata = 'alt'),
                        IntegerField('field6', schemata = 'alt')
                        ),)
        
    def assertSchemataOrder(self, schemataName, names):
        """Check field position within field's schemata"""
        fields = self.schema.getSchemataFields(schemataName)
        self.assertEqual([f.getName() for f in fields], names)
        
    def test_moveToBeginning(self):
        moveFieldInSchema(self.schema, 'field2', 0)
        self.assertSchemataOrder('default', ['field2', 'field1', 'field3'])
        moveFieldInSchema(self.schema, 'field6', 0)
        self.assertSchemataOrder('alt', ['field6', 'field4', 'field5'])
                
    def test_moveToEnd(self):
        moveFieldInSchema(self.schema, 'field2', -1)
        self.assertSchemataOrder('default', ['field1', 'field3', 'field2'])
        moveFieldInSchema(self.schema, 'field4', -1)
        self.assertSchemataOrder('alt', ['field5', 'field6', 'field4'])
        
    def test_moveToMiddle(self):
        moveFieldInSchema(self.schema, 'field1', 1)
        self.assertSchemataOrder('default', ['field2', 'field1', 'field3'])
        moveFieldInSchema(self.schema, 'field6', 1)
        self.assertSchemataOrder('alt', ['field4', 'field6', 'field5'])
        
    def test_moveToExistingPosition(self):
        moveFieldInSchema(self.schema, 'field1', 0)
        self.assertSchemataOrder('default', ['field1', 'field2', 'field3'])
        moveFieldInSchema(self.schema, 'field5', 1)
        self.assertSchemataOrder('alt', ['field4', 'field5', 'field6'])
        
    def test_moveToBeginningAndChangeSchemata(self):
        moveFieldInSchema(self.schema, 'field1', 0, 'alt')
        self.assertSchemataOrder('alt', ['field1', 'field4', 'field5', 'field6'])
        
    def test_moveToEndAndChangeSchemata(self):
        moveFieldInSchema(self.schema, 'field6', -1, 'default')
        self.assertSchemataOrder('default', ['field1', 'field2', 'field3', 'field6'])
        

tests.append(TestMoveFieldInSchema)

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
