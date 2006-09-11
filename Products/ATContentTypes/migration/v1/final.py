from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.migration.atctmigrator import TopicMigrator
from Products.ATContentTypes.content.topic import ATTopic
from Products.CMFCore.Expression import Expression
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.config import PROJECTNAME
from Products.Archetypes.ArchetypeTool import fixActionsForType
from Products.CMFDynamicViewFTI.migrate import migrateFTIs
from Products.CMFDynamicViewFTI.fti import fti_meta_type

def atct1_0_1_atct1_0_2(portal):
    """1.0.1 -> 1.0.2
    """
    out = []

    removeListCriteriaFromTextIndices(portal, out)
    fixLocationCriteriaGrammar(portal, out)

    return out


def removeListCriteriaFromTextIndices(portal, out):
    """Text indices can't use list indexes"""
    indices = ['SearchableText', 'Subject', 'Description']
    tool = getToolByName(portal, 'portal_atct', None)
    if tool is not None:
        for index_name in indices:
            try:
                index = tool.getIndex(index_name)
            except AttributeError:
                continue
            criteria = index.criteria
            if 'ATListCriterion' in criteria:
                new_criteria = [c for c in criteria if c != 'ATListCriterion']
                tool.updateIndex(index_name, criteria=tuple(new_criteria))
                out.append('Removed list criterion from text index %s'%index_name)


def fixLocationCriteriaGrammar(portal, out):
    """Fix the grammer in the location criteria description"""
    tool = getToolByName(portal, 'portal_atct', None)
    if tool is not None:
        try:
            index = tool.getIndex('path')
        except AttributeError:
            return
        friendly_name = index.friendlyName
        if friendly_name.startswith("The location an"):
            tool.updateIndex('path', friendlyName="The location of an item in the portal (path)")
            out.append('Updated path index friendly name.')