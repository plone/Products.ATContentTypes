from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Globals import InitializeClass 
from AccessControl import ClassSecurityInfo
import Persistence

from Products.CMFCore.utils import UniqueObject 
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions

configlets = ({
    'id' : 'portal_atct',
    'appId' : 'ATContentTypes',
    'name' : 'ATContentTypes Tool',
    'action' : 'string:${portal_url}/portal_atct/atct_manageTopicSetup',
    'category' : 'Products',
    'permission' : CMFCorePermissions.ManagePortal,
    'imageUrl' : 'tool_icon.gif'
    },
    )

class ATCTTool(UniqueObject, SimpleItem, PropertyManager): 
    """
    """
    
    security = ClassSecurityInfo()
    
    id = 'portal_atct' 
    meta_type= 'ATCT Tool'
    title = 'ATContentTypes Tool'
    plone_tool = 1
        
    manage_options = SimpleItem.manage_options + \
        PropertyManager.manage_options
        
InitializeClass(ATCTTool)
