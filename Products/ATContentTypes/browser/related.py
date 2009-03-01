from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.publisher.browser import BrowserView

from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName


class RelatedItemsView(BrowserView):

    def available(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        return context_state.is_view_template()

    def getInfoFor(self, item):
        wftool = getToolByName(self.context, 'portal_workflow')
        return wftool.getInfoFor(item, 'review_state', '')

    def normalizeString(self, text):
        return queryUtility(IIDNormalizer).normalize(text)

    def use_view_action(self):
        props = getToolByName(self.context, 'portal_properties')
        site = props.get('site_properties')
        return site.get('typesUseViewActionInListings', ())

    def computeRelatedItems(self):
        items = self.context.getRelatedItems()
        mtool = getToolByName(self.context, 'portal_membership')

        res = []
        for d in range(len(items)):
            try:
                obj = items[d]
            except Unauthorized:
                continue
            if obj not in res:
                if mtool.checkPermission('View', obj):
                    res.append(obj)
        return res
