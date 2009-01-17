from unittest import defaultTestLoader
from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest

from Products.ATContentTypes.tests.atcttestcase import ATCTSiteTestCase


class EventCalendarTests(ATCTSiteTestCase):

    def afterSetUp(self):
        folder = self.folder
        event1 = folder[folder.invokeFactory('Event',
            id='ploneconf2007', title='Plone Conf 2007',
            startDate='2007/10/10', endDate='2007/10/12',)]
        event2 = folder[folder.invokeFactory('Event',
            id='ploneconf2008', title='Plone Conf 2008',
            startDate='2008/10/08', endDate='2008/10/10',)]

    def testCalendarView(self):
        view = getMultiAdapter((self.folder, TestRequest()), name='calendar.ics')
        view.update()
        self.assertEqual(len(view.events), 2)
        self.assertEqual(sorted([ e.Title for e in view.events ]),
            ['Plone Conf 2007', 'Plone Conf 2008'])


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

