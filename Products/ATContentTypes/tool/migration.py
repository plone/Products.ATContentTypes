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
__author__  = 'Christian Heimes <ch@comlounge.net>'

import os, sys, traceback
from cStringIO import StringIO
import logging
import time

from ExtensionClass import Base
from Globals import InitializeClass
from ZODB.POSException import ConflictError
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Acquisition import aq_inner
import AccessControl.Owned
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFPlone import transaction

from Products.CMFCore.utils import UniqueObject 
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import format_stx
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.permissions import View
from Products.CMFCore.ActionProviderBase import ActionProviderBase

from Products.Archetypes import listTypes

from Products.ATContentTypes.interfaces import IATContentType
from Products.ATContentTypes.interfaces import IImageContent
from Products.ATContentTypes.interfaces import IATCTTool
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.config import ATCT_DIR
from Products.ATContentTypes.config import WWW_DIR
from Products.ATContentTypes.migration.atctmigrator import migrateAll
from Products.ATContentTypes.tool.topic import ATTopicsTool

try:
    from ProgressHandler import ZLogHandler
except ImportError:
    def ZLogHandler(*args, **kwargs):
        return False

def timeit(data=None):
    """Measure real time and cpu time of an event
    
    returns real time, cpu time as tuple
    """
    if data is None:
        return time.time(), time.clock()
    else:
        return time.time() - data[0], time.clock() - data[1]

CMF_PRODUCTS = ('CMFPlone', 'CMFDefault', 'CMFTopic', 'CMFCalendar')
ATCT_PRODUCTS = ('ATContentTypes', )
SITE_TYPES = ('Portal Site', 'Plone Site',)

LOG = logging.getLogger('ATCT.migration')

class AlreadySwitched(RuntimeError): pass

class ATCTMigrationTool(Base):
    """ATContentTypes migration methods for the ATCT tool
    """
    
    security = ClassSecurityInfo()
        
    _cmfTypesAreRecataloged = False
    
    __implements__ = ()
        
    manage_options =  (
            {'label' : 'Type Migration', 'action' : 'manage_typeMigration'},
            {'label' : 'Recatalog', 'action' : 'manage_recatalog'},
        )
    
    security.declareProtected(ManagePortal,
                              'manage_recatalog')
    manage_recatalog = PageTemplateFile('recatalog', WWW_DIR)

    security.declareProtected(ManagePortal,
                              'manage_typemigration')
    manage_typeMigration = PageTemplateFile('typeMigration', WWW_DIR)


    security.declareProtected(ManagePortal, 'getCMFTypesAreRecataloged')
    def getCMFTypesAreRecataloged(self):
        """Get the is recatalog flag
        """
        return bool(self._cmfTypesAreRecataloged)
    
    security.declareProtected(ManagePortal, 'setCMFTypesAreRecataloged')
    def setCMFTypesAreRecataloged(self, value=True):
        """set the is recatalog flag
        """
        self._cmfTypesAreRecataloged = value

    security.declareProtected(ManagePortal, 'recatalogCMFTypes')
    def recatalogCMFTypes(self, remove=True):
        """Remove and recatalog all CMF core products + CMFPlone types
        """
        if remove:
            rres, relapse, rc_elapse = self._removeCMFtypesFromCatalog()
        else:
            rres, relapse, rc_elapse = None, 0, 0
        cres, celapse, cc_elapse = self._catalogCMFtypes()
        elapse = relapse + celapse
        c_elapse = rc_elapse + cc_elapse
        return elapse, c_elapse
 
    security.declareProtected(ManagePortal, 'recatalogATCTTypes')
    def recatalogATCTTypes(self, remove=False):
        """Remove and recatalog all ATCT types
        """
        if remove:
            rres, relapse, rc_elapse = self._removeATCTtypesFromCatalog()
        else:
            rres, relapse, rc_elapse = None, 0, 0
        cres, celapse, cc_elapse = self._catalogATCTtypes()
        elapse = relapse + celapse
        c_elapse = rc_elapse + cc_elapse
        return elapse, c_elapse

    # type switching and migration

    security.declareProtected(ManagePortal, 'disableCMFTypes')
    def disableCMFTypes(self):
        """Disable and rename CMF types
        
        You *should* run recatalogCMFTypes() before running this method to make
        sure all types are found!
        
        * Backups the old FTIs as "CMF Name"
        * Changes the portal_type of all existing objects
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
            cmf_orig_pt = klass.portal_type
            cmf_bak_pt = ntf.get('portal_type')
            cmf_mt = ntf.get('meta_type')
            __traceback_info__ = 'Error converting %s to %s in disableCMFTypes'%(
                                            str(cmf_orig_pt), str(cmf_bak_pt))
            error = self._changePortalTypeName(cmf_orig_pt, cmf_bak_pt, global_allow=False,
                                       meta_type=cmf_mt)
            if not error:
                result.append('Renamed %s to %s' % (cmf_orig_pt, cmf_bak_pt))
        return ''.join(result)
    
    security.declareProtected(ManagePortal, 'enableCMFTypes')
    def enableCMFTypes(self):
        """Enable CMF types
        
        NOTE: Enabling CMF types leaves all ATCT based types in an insane state!
        
        Maybe we should rename the types:
        
            atct_bak_pt = 'AT %s' % cmf_pt
            self._changePortalTypeName(cmf_pt, atct_bak_pt, global_allow=False)
        
        The feature isn't in the code because we don't support uninstall.
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
            cmf_orig_pt = klass.portal_type
            cmf_bak_pt = ntf.get('portal_type')
            cmf_mt = ntf.get('meta_type')
            ttool.manage_delObjects(cmf_orig_pt)
            result.append('Removing ATCT: %s' % cmf_orig_pt)
            __traceback_info__ = 'Error converting %s to %s in enableCMFTypes'%(
                                            str(cmf_bak_pt), str(cmf_orig_pt))
            self._changePortalTypeName(cmf_bak_pt, cmf_orig_pt, global_allow=False, meta_type=cmf_mt)
            result.append('Renamed %s to %s' % (cmf_bak_pt, cmf_orig_pt))
        return ''.join(result)
    
    security.declareProtected(ManagePortal, 'copyFTIFlags')
    def copyFTIFlags(self):
        """Copies some flags like allow discussion from the old types to new
        """
        assert self.isCMFdisabled()
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
            atct_pt = klass.portal_type
            cmf_bak_pt = ntf.get('portal_type')
            __traceback_info__ = 'Error converting %s to %s in copyCMFTypes'%(
                                            str(cmf_bak_pt), str(atct_pt))
            self._copyFTIFlags(ptfrom=cmf_bak_pt, ptto=atct_pt)
    
    security.declareProtected(ManagePortal, 'isCMFdisabled')
    def isCMFdisabled(self):
        """Query if CMF types are disabled
        """
        ttool = getToolByName(self, 'portal_types')
        if 'Document' in ttool.objectIds():
            docp = getattr(ttool, 'Document').product
            if docp == 'ATContentTypes':
                return True
        return False

    security.declareProtected(ManagePortal, 'migrateToATCT')
    def migrateToATCT(self, portal_types=None):
        """Migrate to ATCT (all in one)
        
        This method is called from the CMFPlone migration system in order to migrate
        all content types to ATCT based types. For large sites you might want to run
        migration, update workflow and update catalog in three transactions.
        """
        out, elapse, c_elapse = self.migrateContentTypesToATCT(portal_types=None)
        count, elapse, c_elapse = self.migrationUpdateWorkflowRoleMapping()
        out += '\n\nWorkflow: %d object(s) updated.\n' % count
        dummy, elapse, c_elapse = self.migrationRefreshPortalCatalog()
        self.upgrade()
        return out
    
    security.declareProtected(ManagePortal, 'migrateContentTypesToATCT')
    def migrateContentTypesToATCT(self, portal_types=None):
        """Content type migration from CMF types to ATCT  types
        """
        if portal_types is not None:
            # TODO: not impelemented
            raise NotImplementedError, "Migrating a subset of types is not implemented"
        if isinstance(portal_types, basestring):
            portal_types = (portal_types,)
        portal = getToolByName(self, 'portal_url').getPortalObject()
        
        timeinfo = timeit()
        
        out = migrateAll(portal)
        
        elapse, c_elapse = timeit(timeinfo)
    
        LOG.debug('Migrated content types to ATContentType based types '
            'in %s seconds (cpu %s seconds)' % (elapse, c_elapse))
        
        return out, elapse, c_elapse

    security.declareProtected(ManagePortal, 'migrationRefreshPortalCatalog')
    def migrationRefreshPortalCatalog(self):
        """Migration helper - refresh catalog w/ pghandler
        """
        LOG.debug('Updating portal_catalog')
        
        catalog = getToolByName(self, 'portal_catalog')
        timeinfo = timeit()

        try:
            pgthreshold = catalog._getProgressThreshold()
        except AttributeError:
            catalog.refreshCatalog(clear=1)
        else:
            handler = (pgthreshold > 0) and ZLogHandler(pgthreshold) or None
            catalog.refreshCatalog(clear=1, pghandler=handler)

        elapse, c_elapse = timeit(timeinfo)
        
        LOG.debug('Updated and recataloged portal_catalog '
            'in %s seconds (cpu %s seconds)' % (elapse, c_elapse))
            
        return '', elapse, c_elapse
    
    security.declareProtected(ManagePortal, 'migrationUpdateWorkflowRoleMapping')
    def migrationUpdateWorkflowRoleMapping(self):
        """Migration helper - update workflow role mappings
        """
        LOG.debug('Updating workflow role mapping')
        
        wf = getToolByName(self, 'portal_workflow')
        timeinfo = timeit()
        
        count = wf.updateRoleMappings()
        
        elapse, c_elapse = timeit(timeinfo)
        
        LOG.debug('Updated workflow role mappings for %s objects '
            'in %s seconds (cpu %s seconds)' % (count, elapse, c_elapse))
        
        return count, elapse, c_elapse
        
    security.declareProtected(ManagePortal, 'migrationFixCMFPortalTypes')
    def migrationFixCMFPortalTypes(self):
        """Fix portal type name of CMF based objects
        
        Use Case:
            The migration system renames all CMF FTI from e.g. Document to
            CMF Document. In the progress of FTI renaming the portal_type name
            of all object based on these FTIs is reset to the new name, too.
            
            If you copy or import a set of objects with the old type names you
            have to fix the portal_type name because a CMF Document might have
            a portal_type of Document. But Document is an ATDocument. 
        """
        timeinfo = timeit()
        result = []
        
        for fti in self._getCMFFtis():
            id = fti.getId()
            if not id.startswith('CMF '):
                # not a renamed portal type
                continue
            old_name = id[4:]
            new_name = id
            meta_type = fti.content_meta_type
            changed = self._fixPortalTypeOfObjects(old_name, new_name, meta_type)
            result.extend(changed)
        
        elapse, c_elapse = timeit(timeinfo)
        return '\n'.join(result), elapse, c_elapse

    # ************************************************************************
    # private methods

    def _getFtis(self, products = None):
        """Get FTIs by product
        """
        ttool = getToolByName(self, 'portal_types')
        if products is None:
            return ttool.listTypeInfo()
        ftis = []
        for fti in ttool.listTypeInfo():
            product = getattr(aq_base(fti), 'product', None)
            if product in products:
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

    def _getATCTMetaTypes(self):
        """Get all meta_types registered by ATCT
        """
        meta_types = {}
        for fti in self._getATCTFtis():
            mt = getattr(aq_base(fti), 'content_meta_type')
            meta_types[mt] = 1
        return meta_types.keys()

    def _getCMFPortalTypes(self, meta_type=None):
        """Get all portal types registered by CMF core products + CMFPlone for types
        """
        if meta_type is None:
            return [fti.getId() for fti in self._getCMFFtis()]
        else:
            return [fti.getId() for fti in self._getCMFFtis()
                    if aq_base(fti).content_meta_type == meta_type
                   ]

    def _removeTypesFromCatalogByMetatype(self, mt, count=True):
        """Removes all types from the catalog
        
        It's using the meta_type to find all objects.
        """
        if not mt:
            # XXX: I consider passing an empty mt argument as bug
            return 0, 0, 0
        LOG.debug('Remove object by metatypes %s from portal_catalog' %
                            ', '.join(mt))
        
        cat = getToolByName(self, 'portal_catalog')
        counter = 0
        
        timeinfo = timeit()
        
        for brain in cat(meta_type=mt):
            cat.uncatalog_object(brain.getPath())
            counter+=1
            
        elapse, c_elapse = timeit(timeinfo)
        
        LOG.debug('Removed %s objects from portal_catalog '
            'in %s seconds (cpu %s seconds)' % (count, elapse, c_elapse))
        
        return counter, elapse, c_elapse
    
    def _catalogTypesByMetatype(self, mt):
        """Catalogs objects by meta type
        
        It's using the meta_type to find all objects. The objects are found
        by zcatalog's ZopeFindAndApply method. It may take a very (!) long
        time to find all objects.
        """
        if not mt:
            # XXX: I consider passing an empty mt argument as bug
            return [], 0, 0
        
        if not isinstance(mt, (list, tuple)):
            mt = (mt, )
        
        LOG.debug('Catalog object by metatypes %s using '
                            'ZopeFindAndApply' %  ', '.join(mt))
        
        cat = getToolByName(self, 'portal_catalog')
        portal = getToolByName(self, 'portal_url').getPortalObject()
        basepath = '/'.join(portal.getPhysicalPath())
        
        timeinfo = timeit()

        results = self.ZopeFindAndApply(portal,
                                        obj_metatypes=mt,
                                        search_sub=1,
                                        REQUEST=self.REQUEST,
                                        apply_func=cat.catalog_object,
                                        apply_path=basepath)

        elapse, c_elapse = timeit(timeinfo)
        
        LOG.debug('Catalog objects by metatype '
            'in %s seconds (cpu %s seconds)' % (elapse, c_elapse))
        
        return results, elapse, c_elapse
 
    def _removeCMFtypesFromCatalog(self, count=False):
        mt = self._getCMFMetaTypes()
        return self._removeTypesFromCatalogByMetatype(mt, count)
    
    def _catalogCMFtypes(self):
        mt = self._getCMFMetaTypes()
        return self._catalogTypesByMetatype(mt)
 
    def _removeATCTtypesFromCatalog(self, count=False):
        mt = self._getATCTMetaTypes()
        return self._removeTypesFromCatalogByMetatype(mt, count)
    
    def _catalogATCTtypes(self):
        mt = self._getATCTMetaTypes()
        return self._catalogTypesByMetatype(mt)
    
    def _changePortalTypeName(self, old_name, new_name, global_allow=None,
        title=None, meta_type=None):
        """Changes the portal type name of an object

        * Changes the id of the portal type inside portal types
        * Updates the catalog indexes and metadata
        """
        LOG.debug("Changing portal type name from %s to %s" % 
                            (old_name, new_name))

        ttool = getToolByName(self, 'portal_types')

        # Make sure the type we wish to rename exists
        orig_type = getattr(aq_inner(ttool).aq_explicit, old_name, None)
        if orig_type is None:
            return 1

        ttool.manage_renameObject(old_name, new_name)
        new_type = getattr(ttool.aq_explicit, new_name)
        if global_allow is not None:
            new_type.manage_changeProperties(global_allow=global_allow)
        if title is not None:
            new_type.manage_changeProperties(title=title)
        self._fixPortalTypeOfObjects(old_name, new_name, meta_type)
        return 0

    def _fixPortalTypeOfObjects(self, old_name, new_name, meta_type):
        """Change portal type name of objects using the portal catalog
        
        meta_type can be used to restrict the renaming to objects with a
        certain meta type.
        """
        cat = getToolByName(self, 'portal_catalog')
        changed = []
        query = {'portal_type' : old_name}
        if meta_type is not None:
            query['meta_type'] = meta_type

        for brain in cat(query):
            obj = brain.getObject()
            if not obj:
                continue
            try: state = obj._p_changed
            except: state = 0
            path = brain.getPath()
            changed.append(path)
            __traceback_info__ = (obj, getattr(obj, '__class__', 'no class'),
                                  getattr(obj, 'meta_type', 'no metatype'),
                                  path)
            obj._setPortalTypeName(new_name)
            obj.reindexObject(idxs=['portal_type', 'Type', 'meta_type', ])
            if state is None: obj._p_deativate()
        return changed
            
    def _copyFTIFlags(self, ptfrom, ptto, flags = ('filter_content_types',
                      'allowed_content_types', 'allow_discussion')):
        """Copies different flags from one fti to another
        
        * allow discussion
        * allowed content types
        * filter content types
        * actions
        """
        ttool = getToolByName(self, 'portal_types')
        if isinstance(ptfrom, str):
            ptfrom = getattr(ttool.aq_explicit, ptfrom, None)
        if isinstance(ptto, str):
            ptto = getattr(ttool.aq_explicit, ptto, None)
        # Don't error if we are missing an FTI
        if ptfrom is None or ptto is None:
            return 1
        kw = {}
        for flag in flags:
            kw[flag] = getattr(ptfrom.aq_explicit, flag)
        ptto.manage_changeProperties(**kw)
        
        # create clones
        actions_from = tuple(ptfrom._cloneActions())
        actions_to = list(ptto._cloneActions())
        action_to_ids = [action.getId() for action in actions_to]
        # append unlisted actions to actions_to
        for action in actions_from:
            if action.getId() not in action_to_ids:
                actions_to.append(action)
        ptto._actions = tuple(actions_to)

    def _fixPortalTypeOfMembersFolder(self):
        # Why do I need this hack?
        # probably because of the hard coded and false portal type in Plone :|
        # Members._getPortalTypeName() returns ATBTreeFolder instead of
        # Large Plone Folder
        mt = getToolByName(self, 'portal_membership')
        members = mt.getMembersFolder()
        if members is not None:
            members._setPortalTypeName('Large Plone Folder')
            
InitializeClass(ATCTMigrationTool)
