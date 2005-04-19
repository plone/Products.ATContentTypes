from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.migration.atctmigrator import migrateAll


def zero2_alpha1(portal):
    """0.2 -> 1.0-alpha1
    """
    out = []

    # Add unfriendly_types site property from plone 2.1 for ATTopic use
    addUnfriendlyTypesSiteProperty(portal, out)

    # Migrate Date Criterion to new format
    updateDateCriteria(portal, out)
    
    # Migrate Integer Criterion to new format
    
    # Migrate any lingering CMF types (Topics)
    migrateCMFLeftovers(portal,out)

    return out


def addUnfriendlyTypesSiteProperty(portal, out):
    """Adds unfriendly_types site property."""
    # Types which will be installed as "unfriendly" and thus hidden for search
    # purposes
    BASE_UNFRIENDLY_TYPES = ['ATBooleanCriterion',
                             'ATDateCriteria',
                             'ATDateRangeCriterion',
                             'ATListCriterion',
                             'ATPortalTypeCriterion',
                             'ATReferenceCriterion',
                             'ATSelectionCriterion',
                             'ATSimpleIntCriterion',
                             'ATSimpleStringCriterion',
                             'ATSortCriterion',
                             'Discussion Item',
                             'Plone Site',
                             'TempFolder']

    propTool = getToolByName(portal, 'portal_properties', None)
    if propTool is not None:
        propSheet = getattr(propTool, 'site_properties', None)
        if propSheet is not None:
            if not propSheet.hasProperty('unfriendly_types'):
                propSheet.manage_addProperty('unfriendly_types',
                                             BASE_UNFRIENDLY_TYPES,
                                             'lines')
            out.append("Added 'unfriendly_types' property to site_properties.")

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

def migrateCMFLeftovers(portal, out):
    """Migrate any lingering CMF types"""
    out.append('Migrating remaining CMF Types, this may take a while.')
    out.append(migrateAll(portal))
    out.append('CMF type migration finished')