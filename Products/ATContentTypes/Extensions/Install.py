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
__docformat__ = 'restructuredtext'

from Products.Archetypes import listTypes
from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes.Extensions.utils import install_subskin
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO

from Products.Archetypes.interfaces.base import IBaseFolder
from Products.ATContentTypes.interfaces import IATTopic
from Products.ATContentTypes.interfaces import IATTopicCriterion
from Products.ATContentTypes.interfaces import IATContentType
from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.interfaces import IATCTTool

from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.config import WORKFLOW_FOLDER
from Products.ATContentTypes.config import WORKFLOW_TOPIC
from Products.ATContentTypes.config import WORKFLOW_CRITERIA
from Products.ATContentTypes.config import WORKFLOW_DEFAULT
from Products.ATContentTypes.config import GLOBALS
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.Extensions.utils import setupMimeTypes
from Products.ATContentTypes.Extensions.utils import registerActionIcons

from Products.CMFDynamicViewFTI.migrate import migrateFTIs

def install(self, reinstall):
    out = StringIO()

    qi = getToolByName(self, 'portal_quickinstaller')
    
    # step 1: install tool
    # It's required for migration
    tool = installTool(self, out)
        
    # step 2: recatalog CMF items if installing
    # I've to make sure all CMF types are in the catalog
    # Because it make take a long time on a large site you can add the tool
    # manually and recatalog before installing ATCT or even set the flag to
    # True *ON YOUR OWN RISK*
    if not reinstall:
        if tool.getCMFTypesAreRecataloged():
            print >>out, 'CMF types are marked as catalog, no recataloging'
        else:
            print >>out, 'Recataloging CMF types'
            #print 'Recataloging CMF types, this make take a while ...'
            tool.recatalogCMFTypes()
            #print 'Done'
            tool.setCMFTypesAreRecataloged(True)
            # Fix objects with missing portal_type
            tool.fixObjectsWithMissingPortalType()
    
    # step 3: Rename and move away to old CMF types on install
    if not reinstall:
        if not tool.isCMFdisabled():
            print >>out, 'Disable CMF types. They are backuped as "CMF Document" ...'
            tool.disableCMFTypes()
    
    # step 4: Install dependency products 
    installable = [ prod['id'] for prod in qi.listInstallableProducts() ]
    installed = [ prod['id'] for prod in qi.listInstalledProducts() ]
    
    for product in ('ATReferenceBrowserWidget', 'Marshall'):
        if product not in installable + installed:
            raise RuntimeError('%s not available' % product)
        if product in installable:
            qi.installProduct(product)
            print >>out, 'Install %s' % product
    

    # step 5: install skins
    install_subskin(self, out, GLOBALS)

    # step 6: install types
    typeInfo = listTypes(PROJECTNAME)
    installTypes(self, out,
                 typeInfo,
                 PROJECTNAME)

    # step 7: copy fti flags like allow discussion
    if not reinstall:
        print >>out, 'Copying FTI flags like allow_discussion'
        tool.copyFTIFlags()
    
    # step 8: migrate FTIs  to DynamicViewFTIs
    migrated = migrateFTIs(self, product=PROJECTNAME)
    print >>out, "Switch to DynamicViewFTI: %s" % ', '.join(migrated)

    # step 9: changing workflow
    if not reinstall:
        print >>out, 'Workflows setup'
        setupWorkflows(self, typeInfo, out)

    # step 10: setup content type registry
    if not reinstall:
        print >>out, 'Content Type Registry setup'
        old = ('link', 'news', 'document', 'file', 'image')
        setupMimeTypes(self, typeInfo, old=old, moveDown=(IATFile,), out=out)
    
    # step 11: add additional action icons
    print >>out, 'Adding additional action icons'
    registerActionIcons(self, out)
    
    # step 12: set initial version at 0.2 to ensure full migration
    nv, v = tool.getVersion()
    if not nv and not v:
        tool.setInstanceVersion('0.2.0-final ')

    # step 13: run any migrations
    if reinstall:
        print >>out, 'Migrating existing content to latest version'
        migration_result = tool.upgrade()
        print >>out, migration_result
    
    # step 14: add marshallers
    mr = getToolByName(self, 'marshaller_registry')
    if not reinstall or not mr.objectIds():
        setupMarshallPredicates(mr, out)
    
    # step 14: cleanup depr. external methods
    removeExteneralMethods(self, out)
    
    print >> out, 'Successfully installed %s' % PROJECTNAME
    return out.getvalue()

def uninstall(self, reinstall):
    out = StringIO()
    tool = installTool(self, out)
    qi = getToolByName(self, 'portal_quickinstaller')

    # replace ATCT types with CMF types if uninstalling
    if not reinstall:
        assert tool.isCMFdisabled()
        tool.enableCMFTypes()
    
    return out.getvalue()

# QI Hooks
def afterInstall(self, product, reinstall):
    out = StringIO()
    if not reinstall:
        removeCMFTypesFromRegisteredTypes(self, product, out)
    return out.getvalue()

def beforeUninstall(self, cascade, product, reinstall):
    out = StringIO()
    if not reinstall:
        removeCMFTypesFromRegisteredTypes(self, product, out)
    return out.getvalue(), cascade

def installTool(self, out):
    """Install the portal_atct tool
    """
    tool = getToolByName(self, TOOLNAME, None)
    if tool is not None and not IATCTTool.isImplementedBy(tool):
        # tool exists but it invalid - remove it
        self.manage_delObjects([TOOLNAME])
        tool = None
    if tool is None:
        print >>out, "Installing %s" % TOOLNAME
        addTool = self.manage_addProduct['ATContentTypes'].manage_addTool
        addTool('ATCT Tool')
        tool = getToolByName(self, TOOLNAME)
    
    # init tool
    result = tool._initializeTopicTool()
    if result:
        print >>out, 'Initialized Topic Tool'
    
    # register tool as action provider, multiple installs are harmeless
    # currently NOT used
    #actions_tool = getToolByName(self, 'portal_actions')
    #actions_tool.addActionProvider(TOOLNAME)
    
    # register ATCT tool as configlet 
    group = 'atct|ATContentTypes|ATCT Setup'
    cp = getToolByName(self, 'portal_controlpanel')
    if 'atct' not in cp.getGroupIds():
        cp._updateProperty('groups', tuple(cp.groups)+(group,))
    for configlet in tool.getConfiglets():
        cp.unregisterConfiglet(configlet['id'])
    cp.registerConfiglets(tool.getConfiglets())
    
    return tool

def removeCMFTypesFromRegisteredTypes(self, qi_product, out):
    """Alters the Quickinstaller product information
    
    The backups of the CMF types are removed from the list of registered
    type informations. QI won't remove them on uninstall. 
    """
    qi_types = qi_product.types
    atct = getToolByName(self, TOOLNAME)
    cmf_types = atct._getCMFPortalTypes()
    new_types = [ t for t in qi_types if t not in cmf_types]
    qi_product.types = new_types
    print >>out, ('Changing registered type list from %s to %s in '
                  'order to save backed up cmf types' % 
                  (qi_types, new_types))

    return out

def setupWorkflows(self, typeInfo, out):
    """Setup workflow magic
    
    TODO: should be replaced by a proper class attribute and moved to
          Archetypes
    """
    wftool = getToolByName(self, 'portal_workflow')
    for t in typeInfo:
        klass       = t['klass']
        portal_type = t['portal_type']
        if IBaseFolder.isImplementedByInstancesOf(klass) and not \
          IATTopic.isImplementedByInstancesOf(klass):
            setChainFor(portal_type, WORKFLOW_FOLDER, wftool, out)
        elif IATTopic.isImplementedByInstancesOf(klass):
            setChainFor(portal_type, WORKFLOW_TOPIC, wftool, out)
        elif IATTopicCriterion.isImplementedByInstancesOf(klass):
            setChainFor(portal_type, WORKFLOW_CRITERIA, wftool, out)
        elif IATContentType.isImplementedByInstancesOf(klass):
            setChainFor(portal_type, WORKFLOW_DEFAULT, wftool, out)
        else:
            print >>out, 'NOT assigning %s' % portal_type

    # update workflow settings
    count = wftool.updateRoleMappings()

def setChainFor(portal_type, chain, wftool, out):
    """helper method for setupWorkflows
    """
    print >>out, 'Assigning portal type %s with workflow %s' % (portal_type, chain or 'NONE')
    if chain != '(Default)':
        # default is default :)
        wftool.setChainForPortalTypes((portal_type,), chain)

def setupMarshallPredicates(mr, out):
    """setup marshaller
    """
    from Products.Marshall.predicates import add_predicate
    installed = mr.objectIds()
    predicates = [
        { 'id' : 'image_primary', 
          'title' : 'Primary field for images' , 
          'predicate' : 'default', 
          'expression' : "python: object.portal_type == 'Image'",
          'component_name' : 'primary_field'
        },
        { 'id' : 'file_primary', 
          'title' : 'Primary field for files' , 
          'predicate' : 'default', 
          'expression' : "python: object.portal_type == 'File'",
          'component_name' : 'primary_field'
        },
        { 'id' : 'xml_primary', 
          'title' : 'Marshall XML w/ primary field', 
          'predicate' : 'default', 
          'expression' : "python: mode == 'marshall' and object.getContentType().find('xml') != -1",
          'component_name' : 'primary_field'
        },
        { 'id' : 'default_atct', 
          'title' : 'Default marshaller for ATCT', 
          'predicate' : 'default', 
          'expression' : "python: object.meta_type in ('ATDocument', 'ATEvent', 'ATFavorite', 'ATImage', 'ATLink', 'ATNewsItem')",
          'component_name' : 'rfc822'
        },

        ]
    for predicate in predicates:
        if predicate['id'] not in installed:
            add_predicate(mr, **predicate)

def removeExteneralMethods(self, out):
    """Remove deprecated external methods from the portal root
    """
    portal_ids = self.objectIds()
    scripts = (
        'switch_old_plone_types_on', 'switch_old_plone_types_off',
        'migrateFromCMFtoATCT', 'migrateFromCPTtoATCT', 
        'recreateATImageScales', 'switchATCT2CMF', 'switchCMF2ATCT', 
        )
    remove = [script_id for script_id in scripts
              if script_id in portal_ids]
    if remove:
        print  >>out, ("Removing scripts %s from portal root" %
                       ', '.join(remove))
        self.manage_delObjects(remove)
