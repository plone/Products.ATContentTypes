from StringIO import StringIO
#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2005 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
"""
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

from Products.Archetypes import listTypes

from Products.ATContentTypes.interfaces import IATContentType
from Products.ATContentTypes.interfaces import IATImage
from Products.ATContentTypes.interfaces import IATCTTool
from Products.ATContentTypes.config import TOOLNAME

CMF_PRODUCTS = ('CMFPlone', 'CMFDefault', 'CMFTopic', 'CMFCalendar')
ATCT_PRODUCTS = ('ATContentTypes', )
SITE_TYPES = ('Portal Site', 'Plone Site',)

configlets = ({
    'id' : TOOLNAME,
    'appId' : 'ATContentTypes',
    'name' : 'ATContentTypes Tool',
    'action' : 'string:${portal_url}/%s/atct_manageTopicSetup' % TOOLNAME,
    'category' : 'Products',
    'permission' : CMFCorePermissions.ManagePortal,
    'imageUrl' : 'tool_icon.gif'
    },
    )

class AlreadySwitched(RuntimeError): pass

class ATCTTool(UniqueObject, SimpleItem, PropertyManager): 
    """ATContentTypes tool
    
    Used for migration, maintenace ...
    """
    
    security = ClassSecurityInfo()
    
    id = TOOLNAME 
    meta_type= 'ATCT Tool'
    title = 'ATContentTypes Tool'
    plone_tool = True
    
    _cmfTypesAreRecataloged = False
    
    __implements__ = (SimpleItem.__implements__, IATCTTool)
        
    manage_options = SimpleItem.manage_options + \
        PropertyManager.manage_options
        

    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'getCMFTypesAreRecataloged')
    def getCMFTypesAreRecataloged(self):
        """Get the is recatalog flag
        """
        return bool(self._cmfTypesAreRecataloged)
    
    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'setCMFTypesAreRecataloged')
    def setCMFTypesAreRecataloged(self, value=True):
        """set the is recatalog flag
        """
        self._cmfTypesAreRecataloged = value

    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'recreateImageScales')
    def recreateImageScales(self, portal_type=('Image', 'News Item', )):
        """Recreates AT Image scales (doesn't remove unused!)
        """
        out = StringIO()
        print >>out, "Updating AT Image scales"
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog(portal_type = portal_type)
        for brain in brains:
            obj = brain.getObject()
            if not obj: continue

            try: state = object._p_changed
            except: state = 0
    
            field = obj.getField('image')
            if field:
                print >>out, 'Updating %s' % obj.absolute_url(1)
                field.createScales(obj)

            if state is None: object._p_deactivate()
    
        return out.getvalue()

    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'recatalogCMFTypes')
    def recatalogCMFTypes(self):
        """Remove and recatalog all CMF core products + CMFPlone types
        """
        self._removeCMFtypesFromCatalog()
        self._catalogCMFtypes()

    def recatalogATCTTypes(self):
        """Remove and recatalog all ATCT types
        """
        # XXX
        raise NotImplementedError
        
    def disableCMFTypes(self):
        """Disable and rename CMF types
        
        You *should* run recatalogCMFTypes() before running this method to make
        sure all types are found!
        """
        if self.isCMFdisabled():
            raise AlreadySwitched
        result = []
        for atct in self._listATCTTypes():
            klass = atct['klass']
            if not IATContentType.isImplementedByInstancesOf(klass):
                # skip criteria
                continue
            ntf = klass._atct_newTypeFor
            if not ntf or not ntf.get('portal_type'):
                # no old portal type given
                continue
            cmf_pt = ntf.get('portal_type')
            cmf_bak_pt = 'CMF %s' % cmf_pt
            self._changePortalTypeName(cmf_pt, cmf_bak_pt, global_allow=False)
            result.append('Renamed %s to %s' % (cmf_pt, cmf_bak_pt))
        return ''.join(result)
    
    def enableCMFTypes(self):
        """Enable CMF types
        
        XXX: Enabling CMF types leaves all ATCT based types in an insane state!
        """
        assert self.isCMFdisabled()
        result = []
        ttool = getToolByName(self, 'portal_types')
        for atct in self._listATCTTypes():
            klass = atct['klass']
            if not IATContentType.isImplementedByInstancesOf(klass):
                # skip criteria
                continue
            ntf = klass._atct_newTypeFor
            if not ntf or not ntf.get('portal_type'):
                # no old portal type given
                continue
            cmf_pt = ntf.get('portal_type')
            cmf_bak_pt = 'CMF %s' % cmf_pt
            # XXX backup?
            #atct_bak_pt = 'AT %s' % cmf_pt
            #self._changePortalTypeName(cmf_pt, atct_bak_pt, global_allow=False)
            ttool.manage_delObjects(cmf_pt)
            result.append('Removing ATCT: %s' % cmf_pt)
            self._changePortalTypeName(cmf_bak_pt, cmf_pt, global_allow=False)
            result.append('Renamed %s to %s' % (cmf_pt, cmf_bak_pt))
        return ''.join(result)
    
    def isCMFdisabled(self):
        """Query if CMF types are disabled
        """
        ttool = getToolByName(self, 'portal_types')
        if 'Document' in ttool.objectIds():
            docp = getattr(ttool, 'Document').product
            if docp == 'ATContentTypes':
                return True
        return False

    # ************************************************************************
    # private methods

    def _getFtis(self, products = None):
        """Get FTIs by product
        """
        ttool = getToolByName(self, 'portal_types')
        if products is None:
            return ttool.objectValues()
        ftis = []
        for fti in ttool.objectValues():
            product = getattr(aq_base(fti), 'product', None)
            if product in CMF_PRODUCTS:
                if fti.getId() not in SITE_TYPES:
                    ftis.append(fti)
        return ftis
    
    def _getCMFFtis(self):
        """Get all FTIs register by CMF core products + CMFPlone
        
        It includes CMFPlone, CMFDefault, CMFTopic and CMFCalendar
        """
        return self._getFtis(products = CMF_PRODUCTS)

    def _getATCTFtis(self):
        """Get all FTIs register by ATCT
        """
        return self._getFtis(products = ATCT_PRODUCTS)

    def _listATCTTypes(self):
        """Get all atct types
        
        The returned list of dicts contains klass, name, identifer, meta_type,
        portal_type, package, module, schema and signature
        """
        return listTypes('ATContentTypes')
        
    def _getCMFMetaTypes(self):
        """Get all meta_types registered by CMF core products + CMFPlone for types
        """
        meta_types = {}
        for fti in self._getCMFFtis():
            mt = getattr(aq_base(fti), 'content_meta_type')
            meta_types[mt] = 1
        return meta_types.keys()
        
    def _getCMFPortalTypes(self, metatype=None):
        """Get all portal types registered by CMF core products + CMFPlone for types
        """
        if metatype is None:
            return [fti.getId() for fti in self._getCMFFtis()]
        else:
            return [fti.getId() for fti in self._getCMFFtis()
                    if aq_base(fti).content_meta_type == metatype
                   ]

    def _removeTypesFromCatalogByMetatype(self, mt, count=False):
        """Removes all types from the catalog
        
        It's using the meta_type to find all objects.
        """
        cat = getToolByName(self, 'portal_catalog')
        counter = 0
        
        elapse = time.time()
        c_elapse = time.clock()
        
        for brain in cat(meta_type=mt):
            cat.uncatalog_object(brain.getPath())
            if count: counter+=1
            
        elapse = time.time() - elapse
        c_elapse = time.clock() - c_elapse
        
        return counter, elapse, c_elapse
    
    def _removeCMFtypesFromCatalog(self, count=False):
        mt = self._getCMFMetaTypes()
        return self._removeTypesFromCatalogByMetatype(mt, count)
    
    def _catalogTypesByMetatype(self, mt):
        """Catalogs objects by meta type
        
        It's using the meta_type to find all objects. The objects are found
        by zcatalog's ZopeFindAndApply method. It may take a very (!) long
        time to find all objects.
        """
        cat = getToolByName(self, 'portal_catalog')
        portal = getToolByName(self, 'portal_url').getPortalObject()
        basepath = '/'.join(portal.getPhysicalPath())
        
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
    
    def _catalogCMFtypes(self):
        mt = self._getCMFMetaTypes()
        return self._catalogTypesByMetatype(mt)
    
    def _changePortalTypeName(self, old_name, new_name, global_allow=None,
        title=None):
        """Changes the portal type name of an object
        
        Changes the id of the portal type inside portal types
        Also updates the catalog indexes and metadata
        """
        cat = getToolByName(self, 'portal_catalog')
        ttool = getToolByName(self, 'portal_types')

        ttool.manage_renameObject(old_name, new_name)
        new_type = getattr(ttool.aq_explicit, new_name)
        if global_allow is not None:
            new_type.manage_changeProperties(global_allow=global_allow)
        if title is not None:
            new_type.manage_changeProperties(title=title)
        
        brains = cat(portal_type = old_name)
        for brain in brains:
            obj = brain.getObject()
            if not obj:
                continue
            try: state = object._p_changed
            except: state = 0
            #__traceback_info__ = (obj, getattr(obj, '__class__', 'no class'),
            #                      getattr(obj, 'meta_type', 'no metatype'),
            #                      old, new)
            obj._setPortalTypeName(new_name)
            obj.reindexObject(idxs=['portal_type', 'Type', 'meta_type', ])
            if state is None: obj._p_deativate()

    def _fixPortalTypeOfMembersFolder(self):
        # XXX why do I need this hack?
        # probably because of the hard coded and false portal type in Plone :|
        # Members._getPortalTypeName() returns ATBTreeFolder instead of
        # Large Plone Folder
        mt = getToolByName(self, 'portal_membership')
        members = mt.getMembersFolder()
        if members is not None:
            members._setPortalTypeName('Large Plone Folder')
            
InitializeClass(ATCTTool)
