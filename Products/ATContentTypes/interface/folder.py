from zope.interface import Interface
from Products.ATContentTypes.interface.interfaces import IATContentType


class IFilterFolder(Interface):
    def listObjects():
        """
        """

class IATFolder(IATContentType):
    """AT Folder marker interface
    """

class IATBTreeFolder(IATContentType):
    """AT BTree Folder marker interface
    """


