# -*- coding: utf-8 -*-
from Products.ATContentTypes.interfaces.interfaces import IATContentType
from zope.interface import Interface


try:
    from Products.CMFPlone.interfaces.syndication import ISyndicatable
except ImportError:
    from zope.interface import Interface as ISyndicatable


class IFilterFolder(Interface):

    def listObjects():
        """
        """


class IATFolder(IATContentType, ISyndicatable):
    """AT Folder marker interface
    """


class IATBTreeFolder(IATContentType):
    """AT BTree Folder marker interface
    """
