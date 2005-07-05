from Products.Archetypes import listTypes
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.ATContentTypes.migration.atctmigrator import migrateAll
from Products.ATContentTypes.migration.atctmigrator import TopicMigrator
from Products.ATContentTypes.migration.walker import useLevelWalker
from Products.ATContentTypes.criteria import _criterionRegistry
from Products.ATContentTypes.content.topic import ATTopic
from Products.CMFCore.Expression import Expression
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.config import PROJECTNAME
from Products.Archetypes.ArchetypeTool import fixActionsForType

def alpha2_beta1(portal):
    """1.0-alpha2 -> 1.0-beta1
    """
    out = []
    reindex = 0

    # Fix folderlisting action for folderish types
    fixFolderlistingAction(portal, out)

    # Fix folderlisting action for folderish types
    reindex += addRelatedItemsIndex(portal, out)

    # Rename the topics configlet
    renameTopicsConfiglet(portal, out)

    # Update topic actions
    addTopicSyndicationAction(portal, out)

    # Fix up view actions - with CMFDynamicViewFTI, we don't need /view anymore
    fixViewActions(portal, out)

    # switch FTIs to DynamicFTIs
    switchToDynamicFTI(portal, out)

    # ADD NEW STUFF BEFORE THIS LINE!

    # Rebuild catalog
    if reindex:
        reindexCatalog(portal, out)

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


def addTopicSyndicationAction(portal, out):
    """Update the Topic actions"""
    #Do this the lazy way by using fix_actions
    typesTool = getToolByName(portal, 'portal_types', None)
    topicFTI = getattr(typesTool, 'Topic', None)
    if typesTool is not None and topicFTI is not None:
        fixActionsForType(ATTopic, typesTool)
        out.append("Updated Topic actions")
    out.append("Renamed Smart Folder configlet")

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

def switchToDynamicFTI(portal, out):
    """Replace old FTIs with DynamicFTIs.
    
    TODO: Make two methods out of this method. One should have the signatur:
      convertToDynamicFTI(portal, portal_type)
    and should be placed in CMFDynamicViewFTI
    """
    typesTool = getToolByName(portal, 'portal_types')
    atctTool = getToolByName(portal, 'portal_atct')
    
    typeInfo = listTypes(PROJECTNAME)
    for rti in typeInfo:
        klass = rti['klass']
        portal_type = rti['portal_type']
        name = rti['name']
        meta_type = rti['meta_type']
        package = rti['package']
        
        ti = typesTool.getTypeInfo(portal_type)
        if ti is None:
            continue

        typeinfo_name="%s: %s (%s)" % (package, name, meta_type)

        # get the meta type of the FTI from the class, use the default FTI as default
        fti_meta_type = getattr(klass, '_at_fti_meta_type', 
                                FactoryTypeInformation.meta_type)

        if ti.meta_type == fti_meta_type:
            continue

        # copy all data like actions and properties
        actions = []
        for action in getattr(ti, '_actions', ()):
            actions.append(action.copy())
        actions = tuple(actions)
        properties = ti.propdict()
        
        # delete the old fti and create a new one
        typesTool._delObject(portal_type)

        typesTool.manage_addTypeInformation(fti_meta_type,
                                            id=portal_type,
                                            typeinfo_name=typeinfo_name)

        # assign actions and properties from the old fti
        # NOTE: aliases are ignored and security settings are not copied
        new_ti = typesTool[portal_type]
        new_ti._actions = actions
        new_ti.manage_changeProperties(**properties)
        

        out.append("Switched FTI to DynamicFTI for %s" % klass.portal_type)

    out.append("Switched FTIs to DynamicFTIs")
