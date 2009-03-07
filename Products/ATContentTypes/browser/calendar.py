from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface.interfaces import ICalendarSupport
from Products.ATContentTypes.lib import calendarsupport as cs
from plone.memoize import ram


def cachekey(fun, self):
    """ generate a cache key based on the following data:
          * portal URL
          * fingerprint of the brains found in the query
        the returned key is suitable for usage with `memoize.ram.cache` """
    context = aq_inner(self.context)
    def add(brain):
        path = brain.getPath().decode('ascii', 'replace')
        return '%s\n%s\n\n' % (path, brain.modified)
    url = getToolByName(context, 'portal_url')()
    fingerprint = ''.join(map(add, self.events))
    return ''.join((url, fingerprint))


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


class TopicCalendarView(CalendarView):
    """ view (on "topic" content) for aggregating event data into
        an `.ics` feed """

    def update(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        if 'object_provides' in catalog.indexes():
            query = {'object_provides': ICalendarSupport.__identifier__}
        else:
            query = {'portal_type': 'Event'}
        self.events = context.queryCatalog(**query)

