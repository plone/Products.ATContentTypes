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
import urllib
import zLOG

from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Globals import InitializeClass
from ZODB.POSException import ConflictError
from AccessControl import ClassSecurityInfo
import Persistence
from Acquisition import aq_base
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

CMF_PRODUCTS = ('CMFPlone', 'CMFDefault', 'CMFTopic', 'CMFCalendar')
ATCT_PRODUCTS = ('ATContentTypes', )
SITE_TYPES = ('Portal Site', 'Plone Site',)

LOG_MIGRATION = logging.getLogger('ATCT.migration')
LOG = logging.getLogger('ATContentTypes')

configlets = ({
    'id' : TOOLNAME,
    'appId' : 'ATContentTypes',
    'name' : 'Smart Folder Settings',
    'action' : 'string:${portal_url}/%s/atct_manageTopicIndex' % TOOLNAME,
    'category' : 'Plone',
    'permission' : ManagePortal,
    'imageUrl' : 'topic_icon.gif'
    },
    )

_upgradePaths = {}

def registerUpgradePath(oldversion, newversion, function):
    """ Basic register func """
    _upgradePaths[oldversion.lower()] = [newversion.lower(), function]

def log(message,summary='',severity=0):
    zLOG.LOG('ATCT: ', severity, summary, message)

class AlreadySwitched(RuntimeError): pass

class ATCTTool(UniqueObject, SimpleItem, PropertyManager, ActionProviderBase,
    ATTopicsTool):
    """ATContentTypes tool
    
    Used for migration, maintenace ...
    """
    
    security = ClassSecurityInfo()
    
    id = TOOLNAME 
    meta_type= 'ATCT Tool'
    title = 'ATContentTypes Tool'
    plone_tool = True
    
    _cmfTypesAreRecataloged = False
    _numversion = ()
    _version = ''

    _needRecatalog = 0
    
    __implements__ = (SimpleItem.__implements__, IATCTTool,
                      ActionProviderBase.__implements__,
                      ATTopicsTool.__implements__)
        
    manage_options =  (
            {'label' : 'Overview', 'action' : 'manage_overview'},
            {'label' : 'Type Migration', 'action' : 'manage_typeMigration'},
            {'label' : 'Version Migration', 'action' : 'manage_versionMigration'},
            {'label' : 'Recatalog', 'action' : 'manage_recatalog'},
            {'label' : 'Image scales', 'action' : 'manage_imageScales'}
        ) + PropertyManager.manage_options + \
            AccessControl.Owned.Owned.manage_options
            #ActionProviderBase.manage_options + \
            #SimpleItem.manage_options

    security.declareProtected(ManagePortal,
                              'manage_imageScales')
    manage_imageScales = PageTemplateFile('imageScales', WWW_DIR)
    
    security.declareProtected(ManagePortal,
                              'manage_recatalog')
    manage_recatalog = PageTemplateFile('recatalog', WWW_DIR)

    security.declareProtected(ManagePortal,
                              'manage_typemigration')
    manage_typeMigration = PageTemplateFile('typeMigration', WWW_DIR)

    security.declareProtected(ManagePortal,
                              'manage_versionMigration')
    manage_versionMigration = PageTemplateFile('versionMigration', WWW_DIR)


    security.declareProtected(ManagePortal,
                              'manage_overview')
    manage_overview = PageTemplateFile('overview', WWW_DIR)
    
    ## version code

    security.declareProtected(ManagePortal, 'setInstanceVersion')
    def setInstanceVersion(self, version):
        """ The version this instance of atct is on """
        self._version = version

        vers, rest = version.split(' ')
        major, minor, bugfix =  vers.split('.')
        bugfix, release = bugfix.split('-')

        self._numversion = (int(major), int(minor), int(bugfix), -199)

    security.declareProtected(ManagePortal, 'setVersionFromFS')
    def setVersionFromFS(self):
        """Updates internal numversion and version from FS
        """
        self._numversion, self._version = self.getVersionFromFS()
    
    security.declareProtected(ManagePortal, 'getVersionFromFS')
    def getVersionFromFS(self):
        """Get numversion and version from FS
        """
        from Products.ATContentTypes import __pkginfo__ as pkginfo 
        return pkginfo.numversion, pkginfo.version.lower()

    security.declareProtected(ManagePortal, 'getVersion')
    def getVersion(self):
        """Get internal numversion and version
        """
        return self._numversion, self._version
 
    security.declareProtected(View, 'needsVersionMigration')
    def needsVersionMigration(self):
        """Version migration is required when fs version != installed version
        """
        nv, v = self.getVersion()
        fsnv, fsv = self.getVersionFromFS()
        if nv != fsnv or v != fsv:
            return True
        return False

    def om_icons(self):
        icons = ({
                    'path':'misc_/ATContentTypes/tool.gif',
                    'alt':self.meta_type,
                    'title':self.meta_type,
                 },)
        if self.needsVersionMigration():
            icons = icons + ({
                     'path':'misc_/PageTemplates/exclamation.gif',
                     'alt':'Error',
                     'title':'ATContentTypes needs updating'
                  },)

        return icons

    security.declareProtected(ManagePortal, 'needRecatalog')
    def needRecatalog(self):
        """ Does this thing now need recataloging? """
        return self._needRecatalog

    security.declareProtected(ManagePortal, 'knownVersions')
    def knownVersions(self):
        """ All known version ids, except current one """
        return _upgradePaths.keys()

    ##############################################################

    security.declareProtected(ManagePortal, 'upgrade')
    def upgrade(self, REQUEST=None, dry_run=None, swallow_errors=1, force_instance_version=None):
        """ perform the upgrade """
        # keep it simple
        out = []

        self._check()

        if force_instance_version is None:
            instance_version = self.getVersion()[1]
        else:
            instance_version = force_instance_version

        if dry_run:
            out.append(("Dry run selected.", zLOG.INFO))

        # either get the forced upgrade instance or the current instance
        newv = getattr(REQUEST, "force_instance_version",
                       instance_version)

        out.append(("Starting the migration from "
                    "version: %s" % newv, zLOG.INFO))
        while newv is not None:
            out.append(("Attempting to upgrade from: %s" % newv, zLOG.INFO))
            try:
                newv, msgs = self._upgrade(newv)
                if msgs:
                    for msg in msgs:
                        # if string make list
                        if type(msg) == type(''):
                            msg = [msg,]
                        # if no status, add one
                        if len(msg) == 1:
                            msg.append(zLOG.INFO)
                        out.append(msg)
                if newv is not None:
                    out.append(("Upgrade to: %s, completed" % newv, zLOG.INFO))
                    self.setInstanceVersion(newv)

            except ConflictError:
                raise
            except:
                out.append(("Upgrade aborted", zLOG.ERROR))
                out.append(("Error type: %s" % sys.exc_type, zLOG.ERROR))
                out.append(("Error value: %s" % sys.exc_value, zLOG.ERROR))
                for line in traceback.format_tb(sys.exc_traceback):
                    out.append((line, zLOG.ERROR))

                # set newv to None
                # to break the loop
                newv = None
                if not swallow_errors:
                    for msg, sev in out: log(msg, severity=sev)
                    raise
                else:
                    # abort transaction to safe the zodb
                    transaction.abort()

        out.append(("End of upgrade path, migration has finished", zLOG.INFO))

        if self.needsVersionMigration():
            out.append((("The upgrade path did NOT reach "
                        "current version"), zLOG.PROBLEM))
            out.append(("Migration has failed", zLOG.PROBLEM))
        else:
            out.append((("Your ATCT instance is now up-to-date."), zLOG.INFO))

        # do this once all the changes have been done
        if self.needRecatalog():
            try:
                self.portal_catalog.refreshCatalog()
                self._needRecatalog = 0
            except ConflictError:
                raise
            except:
                out.append(("Exception was thrown while cataloging",
                            zLOG.ERROR))
                out += traceback.format_tb(sys.exc_traceback)
                if not swallow_errors:
                    for msg, sev in out: log(msg, severity=sev)
                    raise

        if dry_run:
            out.append(("Dry run selected, transaction aborted", zLOG.INFO))
            transaction.abort()

        # log all this to the ZLOG
        for msg, sev in out: log(msg, severity=sev)

        return out

    ##############################################################
    # Private methods

    def _check(self):
        """ Are we inside an ATCT site?  This is probably silly and redundant."""
        if getattr(self, TOOLNAME, []) == []:
            raise AttributeError, 'You must be in an ATCT site to migrate.'

    def _upgrade(self, version):
        version = version.lower()
        # Handle silly spaces after version names
        if not _upgradePaths.has_key(version):
            version=version+" "
            if not _upgradePaths.has_key(version):
                return None, ("Migration completed at version %s" % version,)

        newversion, function = _upgradePaths[version]
        res = function(self.aq_parent)
        return newversion, res


    ## recataloging code

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

    # image scales

    security.declareProtected(ManagePortal, 'recreateImageScales')
    def recreateImageScales(self, portal_type=('Image', 'News Item', )):
        """Recreates AT Image scales (doesn't remove unused!)
        """
        out = StringIO()
        print >>out, "Updating AT Image scales"
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog(portal_type = portal_type)
        for brain in brains:
            obj = brain.getObject()
            if obj is None:
                continue
            
            if not IImageContent.isImplementedBy(obj):
                continue

            try: state = obj._p_changed
            except: state = 0
    
            field = obj.getField('image')
            if field:
                print >>out, 'Updating %s' % obj.absolute_url(1)
                field.createScales(obj)

            if state is None: obj._p_deactivate()
    
        return out.getvalue()

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
            self._changePortalTypeName(cmf_orig_pt, cmf_bak_pt, global_allow=False,
                                       metatype=cmf_mt)
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
            self._changePortalTypeName(cmf_bak_pt, cmf_orig_pt, global_allow=False, metatype=cmf_mt)
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
        elapse, c_elapse, out = self.migrateContentTypesToATCT(portal_types=None)
        elapse, c_elapse, count = self.migrationUpdateWorkflowRoleMapping()
        out += '\n\nWorkflow: %d object(s) updated.\n' % count
        elapse, c_elapse = self.migrationRefreshPortalCatalog()
            
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
        
        elapse = time.time()
        c_elapse = time.clock()
        
        out = migrateAll(portal)
        
        elapse = time.time() - elapse
        c_elapse = time.clock() - c_elapse
    
        LOG_MIGRATION.debug('Migrated content types to ATContentType based types '
            'in %s seconds (cpu %s seconds)' % (elapse, c_elapse))
        
        return elapse, c_elapse, out

    security.declareProtected(ManagePortal, 'migrationRefreshPortalCatalog')
    def migrationRefreshPortalCatalog(self):
        """Migration helper - refresh catalog w/ pghandler
        """
        LOG_MIGRATION.debug('Updating portal_catalog')
        
        catalog = getToolByName(self, 'portal_catalog')
        elapse = time.time()
        c_elapse = time.clock()

        try:
            pgthreshold = catalog._getProgressThreshold()
        except AttributeError:
            catalog.refreshCatalog(clear=1)
        else:
            handler = (pgthreshold > 0) and ZLogHandler(pgthreshold) or None
            catalog.refreshCatalog(clear=1, pghandler=handler)

        elapse = time.time() - elapse
        c_elapse = time.clock() - c_elapse
        
        LOG_MIGRATION.debug('Updated and recataloged portal_catalog '
            'in %s seconds (cpu %s seconds)' % (elapse, c_elapse))
            
        return elapse, c_elapse
    
    security.declareProtected(ManagePortal, 'migrationUpdateWorkflowRoleMapping')
    def migrationUpdateWorkflowRoleMapping(self):
        """Migration helper - update workflow role mappings
        """
        LOG_MIGRATION.debug('Updating workflow role mapping')
        
        wf = getToolByName(self, 'portal_workflow')
        elapse = time.time()
        c_elapse = time.clock()
        
        count = wf.updateRoleMappings()
        
        elapse = time.time() - elapse
        c_elapse = time.clock() - c_elapse
        
        LOG_MIGRATION.debug('Updated workflow role mappings for %s objects '
            'in %s seconds (cpu %s seconds)' % (count, elapse, c_elapse))
        
        return elapse, c_elapse, count

    # utilities

    security.declareProtected(ManagePortal, 'getReadme')
    def getReadme(self, stx_level=4):
        f = open(os.path.join(ATCT_DIR, 'README.txt'))
        return format_stx(f.read(), stx_level)

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

    def _getCMFPortalTypes(self, metatype=None):
        """Get all portal types registered by CMF core products + CMFPlone for types
        """
        if metatype is None:
            return [fti.getId() for fti in self._getCMFFtis()]
        else:
            return [fti.getId() for fti in self._getCMFFtis()
                    if aq_base(fti).content_meta_type == metatype
                   ]

    def _removeTypesFromCatalogByMetatype(self, mt, count=True):
        """Removes all types from the catalog
        
        It's using the meta_type to find all objects.
        """
        LOG_MIGRATION.debug('Remove object by metatypes %s from portal_catalog' %
                            ', '.join(mt))
        
        cat = getToolByName(self, 'portal_catalog')
        counter = 0
        
        elapse = time.time()
        c_elapse = time.clock()
        
        for brain in cat(meta_type=mt):
            cat.uncatalog_object(brain.getPath())
            counter+=1
            
        elapse = time.time() - elapse
        c_elapse = time.clock() - c_elapse
        
        LOG_MIGRATION.debug('Removed %s objects from portal_catalog '
            'in %s seconds (cpu %s seconds)' % (count, elapse, c_elapse))
        
        return counter, elapse, c_elapse
    
    def _catalogTypesByMetatype(self, mt):
        """Catalogs objects by meta type
        
        It's using the meta_type to find all objects. The objects are found
        by zcatalog's ZopeFindAndApply method. It may take a very (!) long
        time to find all objects.
        """
        LOG_MIGRATION.debug('Catalog object by metatypes %s using ZopeFindAndApply' %
                            ', '.join(mt))
        
        cat = getToolByName(self, 'portal_catalog')
        portal = getToolByName(self, 'portal_url').getPortalObject()
        basepath = '/'.join(portal.getPhysicalPath())
        
        elapse = time.time()
        c_elapse = time.clock()

        if mt:
            results = self.ZopeFindAndApply(portal,
                                        obj_metatypes=mt,
                                        search_sub=1,
                                        REQUEST=self.REQUEST,
                                        apply_func=cat.catalog_object,
                                        apply_path=basepath)

        elapse = time.time() - elapse
        c_elapse = time.clock() - c_elapse
        
        LOG_MIGRATION.debug('Catalog objects by metatype '
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
        title=None, metatype=None):
        """Changes the portal type name of an object
        
        * Changes the id of the portal type inside portal types
        * Updates the catalog indexes and metadata
        """
        LOG_MIGRATION.log("TRACE", "Changing portal type name from %s to %s" % 
                            (old_name, new_name))
        
        cat = getToolByName(self, 'portal_catalog')
        ttool = getToolByName(self, 'portal_types')

        ttool.manage_renameObject(old_name, new_name)
        new_type = getattr(ttool.aq_explicit, new_name)
        if global_allow is not None:
            new_type.manage_changeProperties(global_allow=global_allow)
        if title is not None:
            new_type.manage_changeProperties(title=title)

        if metatype is not None:
            brains = cat(portal_type = old_name, meta_type = metatype)
        else:
            brains = cat(portal_type = old_name)
        for brain in brains:
            obj = brain.getObject()
            if not obj:
                continue
            try: state = obj._p_changed
            except: state = 0
            __traceback_info__ = (obj, getattr(obj, '__class__', 'no class'),
                                  getattr(obj, 'meta_type', 'no metatype'),
                                  (getattr(obj, 'getPhysicalPath', None) is not None and
                                  obj.getPhysicalPath()) or 'no context')
            obj._setPortalTypeName(new_name)
            obj.reindexObject(idxs=['portal_type', 'Type', 'meta_type', ])
            if state is None: obj._p_deativate()
            
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
            ptfrom = getattr(ttool.aq_explicit, ptfrom)
        if isinstance(ptto, str):
            ptto = getattr(ttool.aq_explicit, ptto)
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

    security.declarePrivate('getConfiglets')
    def getConfiglets(self):
        """ Returns the list of configlets for this tool """
        return tuple(configlets)
            
InitializeClass(ATCTTool)
