from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.migration.atctmigrator import migrateAll
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.migration.atctmigrator import TopicMigrator
from Products.ATContentTypes.migration.walker import useLevelWalker
from Products.ATContentTypes.criteria import _criterionRegistry


def alpha1_alpha2(portal):
    """0.2 -> 1.0-alpha2
    """
    out = []

    #Remove criteria from catalog
    uncatalogCriteria(portal,out)

    # Migrate Date Criterion to new format
    updateDateCriteria(portal, out)

    # Migrate Integer Criterion to new format
    updateIntegerCriteria(portal,out)
    
    # Migrate any lingering CMF Topics
    migrateCMFTopics(portal,out)

    return out

def findAndAlterCriteria(portal, out, meta_type, func, **kwargs):
    """Searches for all objects of a given meta_type and performs a transformation
       on them using the function passed in the func argument.  The function needs
       to accept the parameters (portal, obj, out) at minimum.  Only works with
       objects in portal_catalog."""
    cat = getToolByName(portal, 'portal_catalog', None)
    if cat is not None:
        brains = cat(meta_type = 'ATTopic')
        for brain in brains:
            obj = brain.getObject()
            for crit in obj.objectValues(meta_type):
                func(portal,crit,out,**kwargs)

def updateDateCriterion(portal,obj,out):
    """Updates a date criterion (obj) to use the new properties scheme"""
    DATE_RANGE = obj.getDateRange()
    old_op = obj.getOperation()
    if old_op == 'max':
        new_op = (DATE_RANGE == '-' and 'more') or 'less'
    elif old_op == 'min':
        new_op = (DATE_RANGE == '-' and 'less') or 'more'
    else:
        new_op = old_op
    obj.setOperation(new_op)
    if new_op != old_op:
        out.append('Date Criterion %s updated to new format'%obj.absolute_url())

def updateDateCriteria(portal, out):
    findAndAlterCriteria(portal, out, 'ATFriendlyDateCriteria',updateDateCriterion)

def updateIntegerCriterion(portal,obj,out):
    """Updates a integer criterion (obj) to use the new properties scheme"""
    #Calling the accessors should trigget getDefault for these new fields
    value2 = obj.getRawValue2()
    direction = obj.getRawDirection()
    obj.setValue2(value2)
    obj.setDirection(direction)
    out.append('Integer Criterion %s updated to new format'%obj.absolute_url())

def updateIntegerCriteria(portal,out):
    findAndAlterCriteria(portal, out, 'ATSimpleIntCriterion',updateIntegerCriterion)

def uncatalogCriteria(portal,out):
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        crits = catalog(meta_type=_criterionRegistry.listTypes())
        if crits:
            out.append('Uncataloging the ATCT criteria.')
        for crit in crits:
            catalog.unindexObject(crit.getObject())

def migrateCMFTopics(portal, out):
    """Migrate any lingering CMF types"""
    out.append('Migrating remaining CMF Types, this may take a while.')
    catalog = getToolByName(portal, 'portal_catalog', None)
    pprop = getToolByName(portal, 'portal_properties', None)
    atct = getToolByName(portal, TOOLNAME, None)
    #Recatalog the CMF Topics if they were missed

    #The portal type for CMF Topics has is now wrong we need to change it back
    if catalog is not None:
        if atct is not None:
            atct.recatalogCMFTypes()
        topics = catalog(meta_type=['Portal Topic'])
        for brain in topics:
            out.append('Changing portal_type for %s'%brain.getPath())
            topic = brain.getObject()
            topic._setPortalTypeName('CMF Topic')
            catalog.reindexObject(topic,idxs=['portal_type', 'Type', 'meta_type', ])

        kwargs = {}
        try:
            kwargs['default_language'] = pprop.aq_explicit.site_properties.default_language
        except (AttributeError, KeyError):
            kwargs['default_language'] = 'en'
        out.append('*** Migrating Topics ***')
        useLevelWalker(portal, TopicMigrator, out=out, **kwargs)
    out.append('CMF type migration finished')