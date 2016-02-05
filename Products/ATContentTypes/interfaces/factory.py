# -*- coding: utf-8 -*-
from zope.interface import Attribute
from zope.interface import Interface


class IFactoryTool(Interface):
    """This tool manages the portal factory type registration.
    """

    id = Attribute('id', 'Must be set to "portal_factory"')

    def getFactoryTypes():
        """Return the list of factory types which use the portal factory.
        """
