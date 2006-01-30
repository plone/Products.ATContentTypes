from zope.interface import implements
from Products.ATContentTypes.interface.dataExtractor import IDataExtractor


class DocumentDataExtractor(object):
    """
    """
    implements(IDataExtractor)
    
    def __init__(self, context):
        self.context = context

    def getData(self,**kwargs):
        """
        """
        return self.context.CookedBody()

class DocumentRawDataExtractor(object):
    """
    """
    implements(IDataExtractor)
 
    def __init__(self, context):
        self.context = context

    def getData(self,**kwargs):
        """
        """
        return self.context.getRawText()
