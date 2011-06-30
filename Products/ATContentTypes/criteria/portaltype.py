from zope.component import queryUtility
from zope.i18n import translate
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory

from AccessControl import ClassSecurityInfo
from Acquisition import aq_get
from Products.Archetypes.atapi import DisplayList
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.criteria import FIELD_INDICES
from Products.ATContentTypes.criteria.selection import ATSelectionCriterion
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion

from Products.ATContentTypes import ATCTMessageFactory as _

ATPortalTypeCriterionSchema = ATSelectionCriterion.schema.copy()
ATPortalTypeCriterionSchema.delField("operator") # https://dev.plone.org/plone/ticket/10882

val_widget = ATPortalTypeCriterionSchema['value'].widget
val_widget.description=_(u'help_portal_type_criteria_value',
                         default=u'One of the available content types.')
ATPortalTypeCriterionSchema['value'].widget = val_widget


class ATPortalTypeCriterion(ATSelectionCriterion):
    """A portal_types criterion"""

    implements(IATTopicSearchCriterion)

    security       = ClassSecurityInfo()
    schema         = ATPortalTypeCriterionSchema
    meta_type      = 'ATPortalTypeCriterion'
    archetype_name = 'Portal Types Criterion'
    shortDesc      = 'Select content types'

    security.declareProtected(View, 'getCurrentValues')
    def getCurrentValues(self):
        """Return enabled portal types"""
        name = u'plone.app.vocabularies.ReallyUserFriendlyTypes'
        types = queryUtility(IVocabularyFactory, name=name)(self)
        portal_types = getToolByName(self, 'portal_types', None)
        request = aq_get(self, 'REQUEST', None)
        result = []
        for term in types.by_value.values():
            value = term.value  # portal_type
            if self.Field() == 'Type':
                # Switch the value from portal_type to archetype_name,
                # since that is stored in the Type-index in portal_catalog
                value = unicode(portal_types[value].title)

            result.append((value, translate(term.title, context=request)))
        def _key(v):
            return v[1]
        result.sort(key=_key)

        return DisplayList(result)

    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []
        if self.Value() is not '':
            result.append((self.Field(), self.Value()))

        return tuple(result)

registerCriterion(ATPortalTypeCriterion, FIELD_INDICES)
