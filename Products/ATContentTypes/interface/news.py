from Products.ATContentTypes.interface.document import IATDocument
from Products.ATContentTypes.interface.image import IImageContent

class IATNewsItem(IATDocument, IImageContent):
    """AT News Item marker interface
    """


