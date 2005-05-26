from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.migration.atctmigrator import migrateAll
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.migration.atctmigrator import TopicMigrator
from Products.ATContentTypes.migration.walker import useLevelWalker
from Products.ATContentTypes.criteria import _criterionRegistry
from Products.CMFCore.Expression import Expression


def alpha2_beta1(portal):
    """1.0-alpha2 -> 1.0-beta1
    """
    out = []

    # Fix folderlisting action for folderish types
    fixFolderlistingAction(portal, out)

    return out

def fixFolderlistingAction(portal, out):
    typesTool = getToolByName(portal, 'portal_types', None)
    if typesTool is not None:
        folderFTI = getattr(typesTool, 'Folder', None)
        if folderFTI is not None:
            haveFolderListing = False
            for action in folderFTI.listActions():
                if action.getId() == 'folderlisting':
                    action.setActionExpression(Expression('string:${folder_url}/view'))
                    action.condition = ''
                    haveFolderListing = True
                    break
            if not haveFolderListing:
                folderFTI.addAction('folderlisting',
                                    'Folder view',
                                    'string:${folder_url}/view',
                                    '',
                                    'View',
                                    'folder',
                                    visible=0)
            out.append("Set target expresion of folderlisting action for 'Folder' to 'view'")
        siteFTI = getattr(typesTool, 'Plone Site', None)
        if siteFTI is not None:
            haveFolderListing = False
            for action in siteFTI.listActions():
                if action.getId() == 'folderlisting':
                    action.setActionExpression(Expression('string:${folder_url}/view'))
                    action.condition = ''
                    haveFolderListing = True
                    break
            if not haveFolderListing:
                siteFTI.addAction('folderlisting',
                                    'Folder view',
                                    'string:${folder_url}/view',
                                    '',
                                    'View',
                                    'folder',
                                    visible=0)
            out.append("Set target expresion of folderlisting action for 'Plone Site' to 'view'")
        topicFTI = getattr(typesTool, 'Topic', None)
        if topicFTI is not None:
            haveFolderListing = False
            for action in topicFTI.listActions():
                if action.getId() == 'folderlisting':
                    action.setActionExpression(Expression('string:${folder_url}/view'))
                    action.condition = ''
                    haveFolderListing = True
                    break
            if not haveFolderListing:
                topicFTI.addAction('folderlisting',
                                    'Folder view',
                                    'string:${folder_url}/view',
                                    '',
                                    'View',
                                    'folder',
                                    visible=0)
            out.append("Set target expresion of folderlisting action for 'Plone Site' to 'view'")
        largefolderFTI = getattr(typesTool, 'Large Plone Folder', None)
        if largefolderFTI is not None:
            haveFolderListing = False
            for action in largefolderFTI.listActions():
                if action.getId() == 'folderlisting':
                    action.setActionExpression(Expression('string:${folder_url}/view'))
                    action.condition = ''
                    haveFolderListing = True
                    break
            if not haveFolderListing:
                largefolderFTI.addAction('folderlisting',
                                    'Folder view',
                                    'string:${folder_url}/view',
                                    '',
                                    'View',
                                    'folder',
                                    visible=0)
            out.append("Set target expresion of folderlisting action for 'Folder' to 'view'")