##############################################################################
#
# ATContentTypes http://sf.net/projects/collective/
# Archetypes reimplementation of the CMF core types
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2003-2005 AT Content Types development team
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Topic:


"""

__author__  = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'

from UserDict import UserDict
from Products.Archetypes.public import registerType
from Products.Archetypes.ClassGen import generateClass
from Products.ATContentTypes.config import PROJECTNAME
from types import StringType

from Products.ATContentTypes.interfaces import IATTopicCriterion
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.interfaces import IATTopicSortCriterion

ALL_INDICES = ('DateIndex', 'DateRangeIndex', 'FieldIndex', 'KeywordIndex',
               'PathIndex', 'TextIndex', 'TextIndexNG2', 'TopicIndex',
               'ZCTextIndex', 'NavtreeIndexNG', 'ExtendedPathIndex')

SORT_INDICES = ('DateIndex', 'DateRangeIndex', 'FieldIndex', 'KeywordIndex')
# TextIndex, PathIndex, TopicIndex, ZCTextIndex, TextIndexNG2, NavtreeIndexNG
# are not usable to sort
# as they do not have 'keyForDocument' attribute

DATE_INDICES = ('DateIndex', 'DateRangeIndex', 'FieldIndex')

STRING_INDICES = ('FieldIndex', 'KeywordIndex', 'PathIndex', 'TextIndex',
                  'TextIndexNG2', 'ZCTextIndex', 'NavtreeIndexNG',
                  'ExtendedPathIndex', 'TopicIndex')

LIST_INDICES = ('FieldIndex', 'KeywordIndex', 'TopicIndex')
FIELD_INDICES = ('FieldIndex',)

class _CriterionRegistry(UserDict):
    """Registry for criteria """

    def __init__(self, *args, **kwargs):
        UserDict.__init__(self, *args, **kwargs)
        self.index2criterion = {}
        self.criterion2index = {}
        self.portaltypes = {}

    def register(self, criterion, indices):
        if type(indices) is StringType:
            indices = (indices,)
        indices = tuple(indices)

        if indices == ():
            indices = ALL_INDICES

        assert IATTopicCriterion.isImplementedByInstancesOf(criterion)
        #generateClass(criterion)
        registerType(criterion, PROJECTNAME)

        id = criterion.meta_type
        self[id] = criterion
        self.portaltypes[criterion.portal_type] = criterion

        self.criterion2index[id] = indices
        for index in indices:
            value = self.index2criterion.get(index, ())
            self.index2criterion[index] = value + (id,)


    def unregister(self, criterion):
        id = criterion.meta_type
        self.pop(id)
        self.criterion2index.pop(id)
        for (index, value) in self.index2criterion.items():
            if id in value:
                valuelist = list(value)
                del valuelist[valuelist.index(id)]
                self.index2criterion[index] = tuple(valuelist)

    def listTypes(self):
        return self.keys()

    def listSortTypes(self):
        return [key for key in self.keys()
                    if IATTopicSortCriterion.isImplementedByInstancesOf(self[key])]

    def listSearchTypes(self):
        return [key for key in self.keys()
                    if IATTopicSearchCriterion.isImplementedByInstancesOf(self[key])]

    def listCriteria(self):
        return self.values()

    def indicesByCriterion(self, criterion):
        return self.criterion2index[criterion]

    def criteriaByIndex(self, index):
        return self.index2criterion[index]
    
    def getPortalTypes(self):
        return tuple(self.portaltypes.keys())

_criterionRegistry = _CriterionRegistry()
registerCriterion = _criterionRegistry.register
unregisterCriterion = _criterionRegistry.unregister

__all__ = ('registerCriterion', 'ALL_INDICES', 'DATE_INDICES', 'STRING_INDICES',
           'LIST_INDICES', 'SORT_INDICES', )

# criteria
import ATDateCriteria
import ATListCriterion
import ATSimpleIntCriterion
import ATSimpleStringCriterion
import ATPortalTypeCriterion
import ATSortCriterion
import ATSelectionCriterion
import ATDateRangeCriterion
import ATReferenceCriterion
import ATBooleanCriterion
