from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import queryUtility
from zope.publisher.browser import BrowserView

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName


class FolderListingView(BrowserView):

    def getInfoFor(self, item):
        wftool = getToolByName(self.context, 'portal_workflow')
        return wftool.getInfoFor(item, 'review_state', '')

    def getMemberInfo(self, creator):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.getMemberInfo(creator)

    def is_a_topic(self):
        return self.context.portal_type == 'Topic'

    def normalizeString(self, text):
        return queryUtility(IIDNormalizer).normalize(text)

    def stx_format(self):
        format = self.context.Format()
        if format in ('text/structured', 'text/x-rst', ):
            return 'stx'
        return 'plain'

    def show_about(self):
        membership = getToolByName(self.context, 'portal_membership')
        anon = membership.isAnonymousUser()
        aava = self.site_properties().get('allowAnonymousViewAbout', False)
        return not anon or aava

    def site_properties(self):
        props = getToolByName(self.context, 'portal_properties')
        return props.get('site_properties')

    def text(self):
        context = self.context
        if getattr(aq_base(context), 'getText', None) is not None:
            return context.getText()
        return None

    def toLocalizedTime(self, time, long_format=None, time_only=None):
        util = getToolByName(self.context, 'translation_service')
        return util.ulocalized_time(
            time, long_format, time_only,context=self.context,
            domain='plonelocales', request=self.request)

    def use_view_action(self):
        return self.site_properties().get('typesUseViewActionInListings', ())
