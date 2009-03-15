from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.sequencebatch import Batch
from zope.component import adapts
from zope.component import queryAdapter
from zope.component import queryUtility
from zope.container.interfaces import IContainer
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.browser import BrowserView

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName


class IFolderContents(Interface):
    """An interface marking a callable adapter, which returns the contents of
    a folder.
    """


class FolderContents(object):

    adapts(IContainer)
    implements(IFolderContents)

    def __init__(self, context):
        self.context = context
        self.__parent__ = context

    def __call__(self, batch=False, b_size=100, b_start=0, full_objects=False):
        context = self.context
        cur_path = '/'.join(context.getPhysicalPath())
        query = dict(
            sort_on='getObjPositionInParent',
            path=dict(query=cur_path, depth=1),
            )

        catalog = getToolByName(context, 'portal_catalog')
        contents = catalog.searchResults(query)
        if len(contents) == 0:
            return ()

        if full_objects:
            contents = [b.getObject() for b in contents]

        if batch:
            return Batch(contents, b_size, b_start, orphan=0)

        return contents


class FolderListingView(BrowserView):

    def folderContents(self):
        b_start = int(self.request.get('b_start', 0))
        b_size = int(self.request.get('limit_display', 100))
        contents = queryAdapter(self.context, IFolderContents)
        return contents(batch=True, b_size=b_size, b_start=b_start)

    def getInfoFor(self, item):
        wftool = getToolByName(self.context, 'portal_workflow')
        return wftool.getInfoFor(item, 'review_state', '')

    def getMemberInfo(self, creator):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.getMemberInfo(creator)

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
