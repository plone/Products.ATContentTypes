import time

from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Globals import InitializeClass 
from AccessControl import ClassSecurityInfo
import Persistence
from Acquisition import aq_base

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
        
    def _getCMFftis(self):
        """Get all FTIs register by CMF core products + CMFPlone
        
        It includes CMFPlone, CMFDefault, CMFTopic and CMFEvent
        """
        products = ('CMFPlone', 'CMFDefault', 'CMFTopic', 'CMFEvent')
        ttool = getToolByName(self, 'portal_types')
        ftis = []
        for fti in ttool.objectValues():
            product = getattr(aq_base(fti), 'product', None)
            if product in products:
                ftis.append(fti)
        return ftis
        
    def _getCMFmetatypes(self):
        """Get all meta_types registered by CMF core products + CMFPlone for types
        """
        meta_types = {}
        for fti in self._getCMFftis():
            mt = getattr(aq_base(fti), 'content_meta_type')
            meta_types[mt] = 1
        return meta_types.keys()
        
    def _getCMFportaltypes(self, metatype=None):
        """Get all portal types registered by CMF core products + CMFPlone for types
        """
        if metatype is None:
            return [fti.getId() for fti in self._getCMFftis()]
        else:
            return [fti.getId() for fti in self._getCMFftis()
                    if aq_base(fti).content_meta_type == metatype
                   ]

    def _removeCMFtypesFromCatalog(self, count=False):
        """Removes all types registered CMF core products + CMFPLone from the catalog
        
        It's using the meta_type to find all objects.
        """
        cat = getToolByName(self, 'portal_catalog')
        mt = self._getCMFmetatypes()
        counter = 0
        
        elapse = time.time()
        c_elapse = time.clock()
        
        for brain in cat(meta_type=mt):
            cat.uncatalog_object(brain.getPath())
            if count: counter+=1
            
        elapse = time.time() - elapse
        c_elapse = time.clock() - c_elapse
        
        return counter, elapse, c_elapse
    
    def _catalogCMFtypes(self):
        """Finds all CMF based types in the site and catalogs it
        
        It's using the meta_type to find all objects. The objects are found
        by zcatalog's ZopeFindAndApply method. It may take a very (!) long
        time to find all objects.
        """
        cat = getToolByName(self, 'portal_catalog')
        portal = getToolByName(self, 'portal_url').getPortalObject()
        basepath = '/'.join(portal.getPhysicalPath())
        mt = self._getCMFmetatypes()
        
        elapse = time.time()
        c_elapse = time.clock()
        
        results = self.ZopeFindAndApply(portal,
                                        obj_metatypes=mt,
                                        search_sub=1,
                                        REQUEST=self.REQUEST,
                                        apply_func=cat.catalog_object,
                                        apply_path=basepath)

        elapse = time.time() - elapse
        c_elapse = time.clock() - c_elapse
        
        return results, elapse, c_elapse

InitializeClass(ATCTTool)
