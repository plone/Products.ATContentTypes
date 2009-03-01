from zope.publisher.browser import BrowserView

from AccessControl import Unauthorized


class RelatedItemsView(BrowserView):

    def computeRelatedItems(self):
        in_out = self.context.getRelatedItems()
        mtool = self.context.portal_membership

        res = []
        for d in range(len(in_out)):
            try:
                obj = in_out[d]
            except Unauthorized:
                continue
            if obj not in res:
                if mtool.checkPermission('View', obj):
                    res.append(obj)
        return res
