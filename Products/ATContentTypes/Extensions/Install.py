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
from Products.ZCatalog.Catalog import CatalogError
from StringIO import StringIO
from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
from Acquisition import aq_base

from Products.Archetypes.interfaces.base import IBaseFolder
from Products.ATContentTypes.interfaces.IATTopic import IATTopic, IATTopicCriterion
from Products.ATContentTypes.interfaces.IATContentType import IATContentType
from Products.ATContentTypes.interfaces.IATFile import IATFile

from Products.ATContentTypes.config import *
from Products.ATContentTypes.Extensions.utils import setupMimeTypes
from Products.ATContentTypes.Extensions.utils import registerTemplates
from Products.ATContentTypes.Extensions.utils import registerActionIcons
from Products.ATContentTypes.Extensions.toolbox import switchATCT2CMF
from Products.ATContentTypes.Extensions.toolbox import isSwitchedToATCT

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
            print 'Recataloging CMF types, this make take a while ...'
            tool.recatalogCMFTypes()
            print 'Done'
            tool.setCMFTypesAreRecataloged(True)
    
    # step 3: Rename and move away to old CMF types on install
    if not reinstall:
        assert not tool.isCMFdisabled()
        print >>out, 'Disable CMF types. They are backuped as "CMF Document" ...'
        tool.disableCMFTypes()
    
    # step 4: Install dependency products 
    installable = [ prod['id'] for prod in qi.listInstallableProducts() ]
    installed = [ prod['id'] for prod in qi.listInstalledProducts() ]
    
    if 'ATReferenceBrowserWidget' not in installable + installed:
        raise RuntimeError('ATReferenceBrowserWidget not available')
    if 'ATReferenceBrowserWidget' in installable:
        qi.installProduct('ATReferenceBrowserWidget')
        print >>out, 'Install ATReferenceBrowserWidget'
    
    if INSTALL_LINGUA_PLONE:
        if 'LinguaPlone' in installable:
            print >>out, 'Installing LinguaPlone as reqested'
            qi.installProduct('LinguaPlone')
            

    # step 5: install types
    typeInfo = listTypes(PROJECTNAME)
    installTypes(self, out,
                 typeInfo,
                 PROJECTNAME)

    # step 6: copy fti flags like allow discussion
    if not reinstall:
        print >>out, 'Copying FTI flags like allow_discussion'
        tool.copyFTIFlags()

    # step 7: install skins
    install_subskin(self, out, GLOBALS)
    
    # step 8: register switch methods to toggle old plonetypes on/off
    # BBB remove these two dummy methods
    manage_addExternalMethod(self,'switchATCT2CMF',
        'DUMMY: Set reenable CMF type',
        PROJECTNAME+'.Install',
        'dummyExternalMethod')
    manage_addExternalMethod(self,'switchCMF2ATCT',
        'DUMMY: Set ATCT as default content types ',
        PROJECTNAME+'.Install',
        'dummyExternalMethod')

    print >> out, 'Successfully installed %s' % PROJECTNAME

    # register switch methods to toggle old plonetypes on/off
    portal=getToolByName(self,'portal_url').getPortalObject()
    manage_addExternalMethod(portal,'switchATCT2CMF',
        'Set reenable CMF type',
        PROJECTNAME+'.toolbox',
        'switchATCT2CMF')
    manage_addExternalMethod(portal,'switchCMF2ATCT',
        'Set ATCT as default content types',
        PROJECTNAME+'.toolbox',
        'switchCMF2ATCT')

    manage_addExternalMethod(portal,'migrateFromCMFtoATCT',
        'Migrate from CMFDefault types to ATContentTypes',
        PROJECTNAME+'.migrateFromCMF',
        'migrate')

    # step 9: changing workflow
    print >>out, 'Workflows setup'
    setupWorkflows(self, typeInfo, out)

    # step 10: setup content type registry
    print >>out, 'Content Type Registry setup'
    old = ('link', 'news', 'document', 'file', 'image')
    setupMimeTypes(self, typeInfo, old=old, moveDown=(IATFile,), out=out)

    # bind templates for TemplateMixin
    registerTemplates(self, typeInfo, out)
    
    # register action icons
    registerActionIcons(self, typeInfo, out)

    removeApplicationXPython(self, out)
    
    # step 11: add additional action icons
    print >>out, 'Adding additional action icons'
    registerActionIcons(self, out)
    
    print >> out, 'Successfully installed %s' % PROJECTNAME
    return out.getvalue()

def uninstall(self, reinstall):
    out = StringIO()
    classes=listTypes(PROJECTNAME)

    # switch back before uninstalling
    if isSwitchedToATCT(self):
        switchATCT2CMF(self)

    # remove external methods for toggling between old and new types
    # leave it for clean up
    for script in ('switch_old_plone_types_on', 'switch_old_plone_types_off',
     'migrateFromCMFtoATCT', 'migrateFromCPTtoATCT', 'recreateATImageScales',
     'switchATCT2CMF', 'switchCMF2ATCT', ):
        if hasattr(aq_base(self), script):
            print >>out, 'Removing script %s from portal root' % script
            self.manage_delObjects(ids=[script,])
    
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
    tool = getToolByName(self, TOOLNAME, None)
    if tool is None:
        addTool = self.manage_addProduct['ATContentTypes'].manage_addTool
        addTool('ATCT Tool')
        tool = getToolByName(self, TOOLNAME)
    print >>out, "Installing %s" % TOOLNAME
    return tool

def removeCMFTypesFromRegisteredTypes(self, product, out):
    qi_types = product.types
    tool = getToolByName(self, TOOLNAME)
    cmf_types = tool._getCMFPortalTypes()
    new_types = [ t for t in qi_types if t not in cmf_types]
    product.types = new_types
    print >>out, 'Changing registered type list from %s to %s in order to' \
                 'save backed up cmf types' % (qi_types, new_types)

    return out

def setupWorkflows(self, typeInfo, out):
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


def dummyExternalMethod(self, *args, **kwargs):
    """Dummy external method for backward compatibility
    """
    return 
