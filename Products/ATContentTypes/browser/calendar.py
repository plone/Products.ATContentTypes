from Acquisition import aq_inner
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface.interfaces import ICalendarSupport
from Products.ATContentTypes.lib import calendarsupport as cs
from plone.memoize import ram


def cachekey(fun, self):
    """ generate a cache key based on the following data:
          * portal URL
          * negotiated language
          * fingerprint of the brains found in the query
        the returned key is suitable for usage with `memoize.ram.cache` """
    context = aq_inner(self.context)
    def add(brain):
        path = brain.getPath().decode('ascii', 'replace')
        return '%s\n%s\n\n' % (path, brain.modified)
    url = getToolByName(context, 'portal_url')()
    state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
    language = state.locale().getLocaleID()
    fingerprint = ''.join(map(add, self.events))
    return ''.join((url, language, fingerprint))


class CalendarView(BrowserView):
    """ view for aggregating event data into an `.ics` feed """

    def update(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        path = '/'.join(context.getPhysicalPath())
        provides = ICalendarSupport.__identifier__
        self.events = catalog(path=path, object_provides=provides)

    def render(self):
        self.update()       # collect events
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        name = '%s.ics' % context.getId()
        request.RESPONSE.setHeader('Content-Type', 'text/calendar')
        request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename="%s"' % name)
        request.RESPONSE.write(self.feeddata())

    @ram.cache(cachekey)
    def feeddata(self):
        data = cs.ICS_HEADER % dict(prodid=cs.PRODID)
        for brain in self.events:
            data += brain.getObject().getICal()
        data += cs.ICS_FOOTER
        return data

    __call__ = render

