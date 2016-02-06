# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.criteria import LIST_INDICES
from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from zope.interface import implements


ATCurrentAuthorSchema = ATBaseCriterionSchema


class ATCurrentAuthorCriterion(ATBaseCriterion):
    """A criterion that searches for the currently logged in user's id"""

    implements(IATTopicSearchCriterion)

    security = ClassSecurityInfo()
    schema = ATCurrentAuthorSchema
    meta_type = 'ATCurrentAuthorCriterion'
    archetype_name = 'Current Author Criterion'
    shortDesc = 'Restrict to current user'

    @security.protected(View)
    def getCriteriaItems(self):
        result = []

        user = getToolByName(
            self, 'portal_membership').getAuthenticatedMember().getId()

        if user is not '':
            result.append((self.Field(), user))

        return tuple(result)

registerCriterion(ATCurrentAuthorCriterion, LIST_INDICES)
