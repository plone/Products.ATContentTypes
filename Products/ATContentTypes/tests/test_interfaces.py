# -*- coding: utf-8 -*-
from Products.ATContentTypes.tool.factory import FactoryTool
from Products.ATContentTypes.tool.factory import TempFolder
from Products.ATContentTypes.tool.metadata import MetadataTool
from Products.CMFPlone.tests.testInterfaces import className
from Products.CMFPlone.tests.testInterfaces import InterfaceTest
from Products.CMFPlone.tests.testInterfaces import zope_interface_test

import unittest


tests = []
# format: (class object, (list interface objects))
testClasses = [
    (FactoryTool, ()),
    (TempFolder, ()),
    (MetadataTool, ()),
]

for testClass in testClasses:
    klass, forcedImpl = testClass
    name = className(klass)
    funcName = 'test%sInterface' % name

    class KlassInterfaceTest(InterfaceTest):
        """ implementation for %s """ % name
        klass = klass
        forcedImpl = forcedImpl

    # add the testing method to the class to get a nice name
    setattr(KlassInterfaceTest, funcName, lambda self: self._testStuff())
    tests.append(KlassInterfaceTest)

    class KlassInterfaceTest(zope_interface_test):
        """ implementation for %s """ % name
        klass = klass
        forcedImpl = forcedImpl

    # add the testing method to the class to get a nice name
    setattr(KlassInterfaceTest, funcName, lambda self: self._testStuff())
    tests.append(KlassInterfaceTest)


def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite
