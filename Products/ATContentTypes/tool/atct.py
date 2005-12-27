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
import zLOG

from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Globals import InitializeClass
from StructuredText.StructuredText import HTML
from ZODB.POSException import ConflictError
from AccessControl import ClassSecurityInfo
import AccessControl.Owned
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFPlone import transaction

from Products.CMFCore.utils import UniqueObject 
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.permissions import View
from Products.CMFCore.ActionProviderBase import ActionProviderBase

from Products.ATContentTypes.interfaces import IImageContent
from Products.ATContentTypes.interfaces import IATCTTool
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.config import ATCT_DIR
from Products.ATContentTypes.config import WWW_DIR
from Products.ATContentTypes.tool.topic import ATTopicsTool
from Products.ATContentTypes.tool.migration import ATCTMigrationTool

try:
    from ProgressHandler import ZLogHandler
except ImportError:
    def ZLogHandler(*args, **kwargs):
        return False

CMF_PRODUCTS = ('CMFPlone', 'CMFDefault', 'CMFTopic', 'CMFCalendar')
ATCT_PRODUCTS = ('ATContentTypes', )
SITE_TYPES = ('Portal Site', 'Plone Site',)

LOG_MIGRATION = logging.getLogger('ATCT.migration')
LOG = logging.getLogger('ATCT')

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

class ATCTTool(UniqueObject, SimpleItem, PropertyManager,
    ActionProviderBase, ATCTMigrationTool, ATTopicsTool):
    """ATContentTypes tool
    
    Used for migration, maintenace ...
    """
    
    security = ClassSecurityInfo()
    
    id = TOOLNAME 
    meta_type= 'ATCT Tool'
    title = 'ATContentTypes Tool'
    plone_tool = True
    # migration
    _numversion = ()
    _version = ''
    _needRecatalog = False
    
    __implements__ = (SimpleItem.__implements__, IATCTTool,
                      ActionProviderBase.__implements__,
                      ATCTMigrationTool.__implements__,
                      ATTopicsTool.__implements__)
        
    manage_options =  (
            {'label' : 'Overview', 'action' : 'manage_overview'},
            {'label' : 'Version Migration', 'action' : 'manage_versionMigration'},
            {'label' : 'Image scales', 'action' : 'manage_imageScales'}
        ) + ATCTMigrationTool.manage_options + \
            PropertyManager.manage_options + \
            AccessControl.Owned.Owned.manage_options
            #ActionProviderBase.manage_options + \
            #SimpleItem.manage_options
    
    # properties and their default values
    
    _properties = PropertyManager._properties + (
        {'id' : 'image_types', 'type' : 'multiple selection',
         'mode' : 'w', 'select_variable' : 'listContentTypes'},
        {'id' : 'folder_types', 'type' : 'multiple selection',
         'mode' : 'w', 'select_variable' : 'listContentTypes'},
        {'id' : 'album_batch_size', 'type' : 'int', 'mode' : 'w'},
        {'id' : 'album_image_scale', 'type' : 'string', 'mode' : 'w'},
        {'id' : 'single_image_scale', 'type' : 'string', 'mode' : 'w'},
        {'id' : 'migration_catalog_patch', 'type' : 'boolean',
         'mode' : 'w'},
        {'id' : 'migration_transaction_size', 'type' : 'int',
         'mode' : 'w'},
        {'id' : 'migration_transaction_style', 'type' : 'selection',
         'mode' : 'w', 'select_variable' : 'transactionStyles'},
        )
    # list of portal types with an Image field used for rescale
    # and album listing
    image_types = ('Image', 'News Item',)
    # list of portal types to display as album folder
    folder_types = ('Folder', 'Large Plone Folder')
    # album batch size
    album_batch_size = 30
    # scale name for image in batch view
    album_image_scale = 'thumb'
    # scale name for image in single view
    single_image_scale = 'preview'
    
    migration_catalog_patch = False
    migration_transaction_size = 20
    migration_transaction_style = None
    transactionStyles = (None, 'full transaction', 'savepoint')
    
    # templates

    security.declareProtected(ManagePortal, 'manage_imageScales')
    manage_imageScales = PageTemplateFile('imageScales', WWW_DIR)
    
    security.declareProtected(ManagePortal, 'manage_versionMigration')
    manage_versionMigration = PageTemplateFile('versionMigration', WWW_DIR)


    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('overview', WWW_DIR)
    
    ## version code

    security.declareProtected(ManagePortal, 'setInstanceVersion')
    def setInstanceVersion(self, version):
        """ The version this instance of atct is on """
        self._version = version
        ver_tup = version.split(' ')
        vers = ver_tup[0]
        rest = len(ver_tup) == 2 and ver_tup[1] or ''

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

    security.declareProtected(ManagePortal, 'needRecatalog')
    def needRecatalog(self):
        """ Does this thing now need recataloging? """
        return self._needRecatalog

    ##############################################################
    # Private methods

    def _check(self):
        """ Are we inside an ATCT site?  This is probably silly and redundant."""
        if getattr(self, TOOLNAME, None) is None:
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

    # image scales

    security.declareProtected(ManagePortal, 'recreateImageScales')
    def recreateImageScales(self, portal_type=None):
        """Recreates AT Image scales (doesn't remove unused!)
        """
        if portal_type is None:
            portal_type = tuple(self.image_types)
        out = StringIO()
        print >>out, "Updating AT Image scales"
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog(portal_type = portal_type,
                         portal_type_operator = 'or')
        for brain in brains:
            obj = brain.getObject()
            if obj is None:
                continue
            
            if not IImageContent.isImplementedBy(obj):
                continue

            try: state = obj._p_changed
            except: state = 0
    
            field = obj.getField('image')
            if field is not None:
                print >>out, 'Updating %s' % obj.absolute_url(1)
                field.removeScales(obj)
                field.createScales(obj)

            if state is None: obj._p_deactivate()
    
        return out.getvalue()

    # utilities

    security.declareProtected(ManagePortal, 'getReadme')
    def getReadme(self, stx_level=4):
        f = open(os.path.join(ATCT_DIR, 'README.txt'))
        return HTML(f.read(), level=stx_level)

    security.declarePrivate('getConfiglets')
    def getConfiglets(self):
        """ Returns the list of configlets for this tool """
        return tuple(configlets)
        
    security.declareProtected(ManagePortal, 'listContentTypes')
    def listContentTypes(self):
        """List all available content types
        
        Used for properties
        """
        ttool = getToolByName(self, 'portal_types')
        return ttool.listContentTypes()
            
InitializeClass(ATCTTool)
