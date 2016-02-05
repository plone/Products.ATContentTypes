# -*- coding: utf-8 -*-
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.tests import atcttestcase
from Products.validation.interfaces.IValidator import IValidationChain


tests = []


class TestBugs(atcttestcase.ATCTSiteTestCase):

    def test_wfmapping(self):
        default = ('plone_workflow',)

        mapping = {
            'Document': default,
            'Event': default,
            'File': (),
            'Folder': ('folder_workflow',),
            'Image': (),
            'Link': default,
            'News Item': default,
            'Collection': default,
        }

        for pt, wf in mapping.items():
            pwf = self.portal.portal_workflow.getChainFor(pt)
            self.assertEqual(pwf, wf, (pt, pwf, wf))

    def test_striphtmlbug(self):
        # Test for Plone tracker #4944
        self.folder.invokeFactory('Document', 'document')
        d = getattr(self.folder, 'document')
        d.setTitle("HTML end tags start with </ and end with >")
        self.assertEqual(
            d.Title(), "HTML end tags start with </ and end with >")

    def test_validation_layer_from_id_field_from_base_schema_was_initialized(
            self):
        field = ATContentTypeSchema['id']
        self.assertTrue(IValidationChain.providedBy(field.validators))
