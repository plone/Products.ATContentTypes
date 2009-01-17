from unittest import defaultTestLoader
from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest

from Products.ATContentTypes.tests.atcttestcase import ATCTSiteTestCase


def makeResponse(request):
    """ create a fake request and set up logging of output """
    headers = {}
    output = []
    class Response:
        def setHeader(self, header, value):
            headers[header] = value
        def write(self, msg):
            output.append(msg)
    request.RESPONSE = Response()
    return headers, output, request


class EventCalendarTests(ATCTSiteTestCase):

    def afterSetUp(self):
        folder = self.folder
        event1 = folder[folder.invokeFactory('Event',
            id='ploneconf2007', title='Plone Conf 2007',
            startDate='2007/10/10', endDate='2007/10/12', location='Naples',
            eventUrl='http://plone.org/events/conferences/2007-naples')]
        event2 = folder[folder.invokeFactory('Event',
            id='ploneconf2008', title='Plone Conf 2008',
            startDate='2008/10/08', endDate='2008/10/10', location='DC',
            eventUrl='http://plone.org/events/conferences/2008-washington-dc')]

    def testCalendarView(self):
        view = getMultiAdapter((self.folder, TestRequest()), name='calendar.ics')
        view.update()
        self.assertEqual(len(view.events), 2)
        self.assertEqual(sorted([ e.Title for e in view.events ]),
            ['Plone Conf 2007', 'Plone Conf 2008'])

    def checkOrder(self, text, *order):
        for item in order:
            position = text.find(item)
            self.failUnless(position >= 0,
                'menu item "%s" missing or out of order' % item)
            text = text[position:]

    def testRendering(self):
        headers, output, request = makeResponse(TestRequest())
        view = getMultiAdapter((self.folder, request), name='calendar.ics')
        view.render()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        self.checkOrder(''.join(output),
            'BEGIN:VCALENDAR',
            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2007',
            'LOCATION:Naples',
            'URL:http://plone.org/events/conferences/2007-naples',
            'END:VEVENT',
            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2008',
            'LOCATION:DC',
            'END:VEVENT',
            'END:VCALENDAR')


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

