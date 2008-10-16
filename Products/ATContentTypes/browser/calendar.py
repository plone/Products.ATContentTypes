from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface.interfaces import ICalendarSupport
from Products.ATContentTypes.lib import calendarsupport as cs


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
        write = request.RESPONSE.write
        write(cs.ICS_HEADER % dict(prodid=cs.PRODID))
        for brain in self.events:
            write(brain.getObject().getICal())
        write(cs.ICS_FOOTER)

    __call__ = render

