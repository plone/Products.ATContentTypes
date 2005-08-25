from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.migration.atctmigrator import TopicMigrator
from Products.ATContentTypes.content.topic import ATTopic
from Products.CMFCore.Expression import Expression
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.config import PROJECTNAME
from Products.Archetypes.ArchetypeTool import fixActionsForType
from Products.CMFDynamicViewFTI.migrate import migrateFTIs
from Products.CMFDynamicViewFTI.fti import fti_meta_type

def alpha2_beta1(portal):
    """1.0-alpha2 -> 1.0-beta1
    """
    out = []

    # Fix folderlisting action for folderish types
    fixFolderlistingAction(portal, out)

    # Fix folderlisting action for folderish types
    reindex = addRelatedItemsIndex(portal, out)
    if reindex:
        reindexIndex(portal, 'getRawRelatedItems', out)

    # Rename the topics configlet
    renameTopicsConfiglet(portal, out)

    # Fix up view actions - with CMFDynamicViewFTI, we don't need /view anymore
    fixViewActions(portal, out)

    # Remove folderContents action from Topics
    removeTopicFolderContentsAction(portal, out)

    # ADD NEW STUFF BEFORE THIS LINE!

    # Rebuild catalog
    if reindex:
        reindexCatalog(portal, out)

    return out

def beta1_rc1(portal):
    """1.0-beta1 -> 1.0.0-rc1
    """
    out = []
    migrateFTIs2DynamicView(portal, out)
    changeDynView2SelectedLayout(portal, out)
    return out

def rc2_rc3(portal):
    """1.0-beta1 -> 1.0.0-rc1
    """
    out = []
    # Make sure Topic uses /edit method alias for edit action
    fixTopicEditAction(portal, out)
    return out

def rc3_rc4(portal):
    """1.0-rc3 -> 1.0.0-rc4
    """
    out = []
    # Update topic actions
    removeTopicSyndicationAction(portal, out)
    return out

def rc5_final(portal):
    """1.0-rc5 -> 1.0.0-final
    """
    out = []
    # Update topic Subjact friendlyname
    changeSubjectToKeywords(portal, out)
    return out

def fixFolderlistingAction(portal, out):
    """Fixes the folder listing action for folderish ATCT types to make it
       work properly with the new browser default magic
    """
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
                return False
            catalog.delIndex('getRawRelatedItems')
            out.append("Deleted %s 'getRawRelatedItems' from portal_catalog." % indextype)

        catalog.addIndex('getRawRelatedItems', 'KeywordIndex')
        out.append("Added KeywordIndex 'getRawRelatedItems' to portal_catalog.")
        return True # Ask for reindexing
    return False


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

def reindexIndex(portal, name, out):
    """Reindex a single index of the portal_catalog."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        # Reduce threshold for the reindex run
        old_threshold = catalog.threshold
        catalog.threshold = 2000
        catalog.reindexIndex(name, REQUEST=portal.REQUEST)
        catalog.threshold = old_threshold
        out.append("Reindexed index %s of portal_catalog." % name)

def renameTopicsConfiglet(portal, out):
    """Update the name of the Topics configlet"""
    tool = getToolByName(portal, TOOLNAME, None)
    if tool is not None:
        group = 'atct|ATContentTypes|ATCT Setup'
        cp = getToolByName(portal, 'portal_controlpanel', None)
        if cp is not None:
            if 'atct' not in cp.getGroupIds():
                cp._updateProperty('groups', tuple(cp.groups)+(group,))
            for configlet in tool.getConfiglets():
                cp.unregisterConfiglet(configlet['id'])
            cp.registerConfiglets(tool.getConfiglets())
    out.append("Renamed Smart Folder configlet")


def removeTopicSyndicationAction(portal, out):
    """Update the Topic actions"""
    #Do this the lazy way by using fix_actions
    typesTool = getToolByName(portal, 'portal_types', None)
    topicFTI = getattr(typesTool, 'Topic', None)
    if typesTool is not None and topicFTI is not None:
        actions = topicFTI.listActions()
        actions = [x for x in actions if x.id != 'syndication']
        topicFTI._actions = tuple(actions)
        out.append("Updated Topic actions")

def fixViewActions(portal, out):
    """Make view actions for types except File and Image not use /view"""
    portal_types = getToolByName(portal, 'portal_types', None)
    if portal_types is not None:
        for t in ('Document', 'Event', 'Favorite', 'Link', 'News Item'):
            fti = portal_types.getTypeInfo(t)
            if fti is not None:
                for action in fti.listActions():
                    if action.getId() == 'view':
                        if action.getActionExpression().endswith('/view'):
                            action.setActionExpression(Expression('string:${object_url}'))
                            out.append("Made %s not use /view for view action" % t)


def removeTopicFolderContentsAction(portal, out):
    """Remove unnecessary folderContents action from Topics"""
    REMOVE_ACTIONS=('folderContents',)
    idxs = []
    idx = 0
    portal_types = getToolByName(portal, 'portal_types', None)
    if portal_types is not None:
        fti = getattr(portal_types, 'Topic', None)
        if fti is not None:
            for action in fti.listActions():
                if action.getId() in REMOVE_ACTIONS:
                    idxs.append(idx)
                    out.append("Removed action %s from Topic FTI"%action.getId())
                idx += 1
            fti.deleteActions(idxs)

def migrateFTIs2DynamicView(portal, out):
    """Migrate FTIs to dynamic view FTI
    """
    result = migrateFTIs(portal, product=PROJECTNAME)
    if result:
        out.append("Migrated FTIs to DynamicView FTI: %s" ', '.join(result))
    else:
        out.append("FTIs are already migrated")

def changeDynView2SelectedLayout(portal, out):
    """Changes the view alias from dyn view to selected layout
    """
    atct = getToolByName(portal, 'portal_atct')
    migrated = []
    for fti in atct._getATCTFtis():
        if getattr(fti, 'meta_type', None) == fti_meta_type:
            aliases = fti.getMethodAliases()
            if aliases.get('view') == '(dynamic view)':
                aliases['view'] = '(selected layout)'
                fti.setMethodAliases(aliases)
                migrated.append(fti.getId())
    if migrated:
        out.append('Migrated view alias to (select layout) for %s' %
                   ', '.join(migrated))

def fixTopicEditAction(portal, out):
    """The topic edit action should be /edit"""
    portal_types = getToolByName(portal, 'portal_types', None)
    if portal_types is not None:
        fti = portal_types.getTypeInfo('Topic')
        if fti is not None:
            for action in fti.listActions():
                if action.getId() == 'edit':
                    if action.getActionExpression().endswith('/atct_edit'):
                        action.setActionExpression(Expression('string:${object_url}/edit'))
                        out.append("Made Topic not use /edit for edit action")

def changeSubjectToKeywords(portal, out):
    """The DC field Subject is called Keywords in Plone"""
    tool = getToolByName(portal, 'portal_atct', None)
    if tool is not None:
        if not tool.getIndex('Subject').friendlyName:
            tool.updateIndex('Subject', friendlyName='Keywords',
            enabled=True, description='The keywords used to describe an item')
            tool.updateMetadata('Subject', friendlyName='Keywords',
            enabled=True, description='The keywords used to describe an item')
            out.append('Updated Smart Folder friendlyName for Subject')