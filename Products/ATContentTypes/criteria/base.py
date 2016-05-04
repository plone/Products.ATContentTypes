# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.Archetypes.atapi import BaseContentMixin
from Products.Archetypes.ClassGen import generateClass
from Products.Archetypes.interfaces.referenceable import IReferenceable
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema
from Products.ATContentTypes.interfaces import IATTopicCriterion
from Products.CMFCore.permissions import View
from zope.interface import classImplementsOnly
from zope.interface import implementedBy
from zope.interface import implements


class NonRefCatalogContent(BaseContentMixin):
    """Base class for content that is neither referenceable nor in the catalog
    """
    isReferenceable = None

    # reference register / unregister methods
    def _register(self, *args, **kwargs): pass

    def _unregister(self, *args, **kwargs): pass

    def _updateCatalog(self, *args, **kwargs): pass

    def _referenceApply(self, *args, **kwargs): pass

    def _uncatalogUID(self, *args, **kwargs): pass

    def _uncatalogRefs(self, *args, **kwargs): pass

    # catalog methods
    def indexObject(self, *args, **kwargs): pass

    def unindexObject(self, *args, **kwargs): pass

    def reindexObject(self, *args, **kwargs): pass

classImplementsOnly(NonRefCatalogContent,
                    *(iface for iface in implementedBy(NonRefCatalogContent)
                      if iface is not IReferenceable))


class ATBaseCriterion(NonRefCatalogContent):
    """A basic criterion"""

    security = ClassSecurityInfo()

    implements(IATTopicCriterion)

    schema = ATBaseCriterionSchema
    meta_type = 'ATBaseCriterion'
    archetype_name = 'Base Criterion'

    def __init__(self, id=None, field=None, oid=None):
        if oid is not None:
            if field is None:
                field = id
            id = oid
        assert id
        NonRefCatalogContent.__init__(self, id)
        if not self.id == id:
            self.id = id
        self.getField('field').set(self, field)

    @security.protected(View)
    def getId(self):
        # Get the object id.
        return str(self.id)

    def setId(self, value, *kw):
        # Setting a new ID isn't allowed.
        assert value == self.getId(), 'You are not allowed to change the id'

    @security.protected(View)
    def Type(self):
        return self.archetype_name

    @security.protected(View)
    def Description(self):
        lines = [line.strip() for line in self.__doc__.splitlines()]
        return ' '.join([line for line in lines if line])

    @security.protected(View)
    def getCriteriaItems(self):
        # Return a sequence of items to be used to build the catalog query.
        return ()

# because I don't register the class I've to generator it on my own. Otherwise
# I'm not able to unit test it in the right way.
generateClass(ATBaseCriterion)
InitializeClass(ATBaseCriterion)
