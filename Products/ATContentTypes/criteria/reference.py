from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.criteria import REFERENCE_INDICES
from Products.ATContentTypes.criteria.selection import ATSelectionCriterion
from Products.ATContentTypes.interface import IATTopicSearchCriterion
from Products.Archetypes.atapi import DisplayList

ATReferenceCriterionSchema = ATSelectionCriterion.schema

class ATReferenceCriterion(ATSelectionCriterion):
    """A reference criterion"""

    implements(IATTopicSearchCriterion)

    security       = ClassSecurityInfo()
    meta_type      = 'ATReferenceCriterion'
    archetype_name = 'Reference Criterion'
    shortDesc      = 'Select referenced content'


    def getCurrentValues(self):
        catalog = getToolByName(self, 'portal_catalog')
        uid_cat = getToolByName(self, 'uid_catalog')
        putils = getToolByName(self, 'plone_utils')
        options = catalog.uniqueValuesFor(self.Field())

        brains = uid_cat(UID=options, sort_on='Title')
        display = []
        for b in brains:
            title_or_id = b.Title or b.id
            display.append(title_or_id.lower(), b.UID, title_or_id)
        display.sort()
        display_list = DisplayList([(d[1], d[2]) for d in display])

        return display_list

registerCriterion(ATReferenceCriterion, REFERENCE_INDICES)
