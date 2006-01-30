# Zope 3 imports
from zope.interface import implements

# fatsyndication imports
from Products.fatsyndication.adapters import BaseFeed, BaseFeedSource, BaseFeedEntry
from Products.basesyndication.interfaces import IFeed, IFeedSource, IFeedEntry


class NewsItemFeedEntry(BaseFeedEntry):
    """
    """

    implements(IFeedEntry)

    def getBody(self):
        """See IFeedEntry.
        """
        return self.context.getBody()

