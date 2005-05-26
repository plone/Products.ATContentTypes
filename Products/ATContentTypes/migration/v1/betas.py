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
    reindex = 0

    # Fix folderlisting action for folderish types
    fixFolderlistingAction(portal, out)

    # Fix folderlisting action for folderish types
    reindex += addRelatedItemsIndex(portal, out)

    # ADD NEW STUFF BEFORE THIS LINE!

    # Rebuild catalog
    if reindex:
        reindexCatalog(portal, out)

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

def addRelatedItemsIndex(portal, out):
    """Adds the getRawRelatedItems KeywordIndex."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        try:
            index = catalog._catalog.getIndex('getRawRelatedItems')
        except KeyError:
            pass
        else:
            indextype = index.__class__.__name__
            if indextype == 'KeywordIndex':
                return 0
            catalog.delIndex('getRawRelatedItems')
            out.append("Deleted %s 'getRawRelatedItems' from portal_catalog." % indextype)

        catalog.addIndex('getRawRelatedItems', 'KeywordIndex')
        out.append("Added KeywordIndex 'getRawRelatedItems' to portal_catalog.")
        return 1 # Ask for reindexing
    return 0

def reindexCatalog(portal, out):
    """Rebuilds the portal_catalog."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        # Reduce threshold for the reindex run
        old_threshold = catalog.threshold
        catalog.threshold = 2000
        catalog.refreshCatalog(clear=1)
        catalog.threshold = old_threshold
        out.append("Reindexed portal_catalog.")