from zope.publisher.browser import BrowserView
from Products.CMFCore.utils import getToolByName

class LinkRedirectView(BrowserView):
    """
    Redirect to the Link target URL, if and only if:
     - redirect_links property is enabled in portal_properties/site_properties
     - AND current user doesn't have permission to edit the Link
    """

    def __call__(self):
        ptool = getToolByName(self.context, 'portal_properties')
        mtool = getToolByName(self.context, 'portal_membership')

        redirect_links = getattr(ptool.site_properties, 'redirect_links', False)
        can_edit = mtool.checkPermission('Modify portal content', self.context)

        if redirect_links and not can_edit:
            return self.request.RESPONSE.redirect(self.context.getRemoteUrl())
        else:
            return self.context.restrictedTraverse('@@link_view')()
