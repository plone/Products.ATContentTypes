# -*- coding: utf-8 -*-
from plone.app.testing.bbb import PloneTestCase


class TestControlPanel(PloneTestCase):

    def afterSetUp(self):
        self.controlpanel = self.portal.portal_controlpanel

        # get the expected configlets
        self.configlets = ['portal_atct']

    def testDefaultConfiglets(self):
        for title in self.configlets:
            self.assertTrue(
                title in [a.getAction(self)['id']
                          for a in self.controlpanel.listActions()],
                "Missing configlet with id '%s'" % title)
