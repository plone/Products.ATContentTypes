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
__author__  = ''
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
from Products.ATContentTypes.interfaces import IATTopic
from Products.ATContentTypes.interfaces import IATTopicCriterion
from Products.ATContentTypes.interfaces import IATContentType
from Products.ATContentTypes.interfaces import IATFile

from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.config import WORKFLOW_FOLDER
from Products.ATContentTypes.config import WORKFLOW_TOPIC
from Products.ATContentTypes.config import WORKFLOW_CRITERIA
from Products.ATContentTypes.config import WORKFLOW_DEFAULT
from Products.ATContentTypes.config import INSTALL_LINGUA_PLONE
from Products.ATContentTypes.config import GLOBALS
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.Extensions.utils import setupMimeTypes
from Products.ATContentTypes.Extensions.utils import registerTemplates
from Products.ATContentTypes.Extensions.utils import registerActionIcons
#from Products.ATContentTypes.Extensions.toolbox import disableCMFTypes
#from Products.ATContentTypes.Extensions.toolbox import enableCMFTypes

def install(self):
    out = StringIO()

    qi = getToolByName(self, 'portal_quickinstaller')
    
    # install tool
    tool = getattr(self.aq_explicit, TOOLNAME, None)
    if tool is None:
        addTool = self.manage_addProduct['ATContentTypes'].manage_addTool
        addTool('ATCT Tool')
        tool = getattr(self.aq_explicit, TOOLNAME)
    
    # step 1: Rename and move away to old CMF types
    if not tool.isCMFdisabled():
        tool.disableCMFTypes()
    #disableCMFTypes(self)
    
    # step 2: Install dependency products 
    
    installable = [ prod['id'] for prod in qi.listInstallableProducts() ]
    installed = [ prod['id'] for prod in qi.listInstalledProducts() ]
    
    if 'ATReferenceBrowserWidget' not in installable + installed:
        raise RuntimeError('ATReferenceBrowserWidget not available')
    if 'ATReferenceBrowserWidget' in installable:
        qi.installProduct('ATReferenceBrowserWidget')
    
    if INSTALL_LINGUA_PLONE:
        if 'LinguaPlone' in installable:
            qi.installProduct('LinguaPlone')

    typeInfo = listTypes(PROJECTNAME)
    installTypes(self, out,
                 typeInfo,
                 PROJECTNAME)

    install_subskin(self, out, GLOBALS)

    print >> out, 'Successfully installed %s' % PROJECTNAME

    # register switch methods to toggle old plonetypes on/off
    
    manage_addExternalMethod(self,'switchATCT2CMF',
        'Set reenable CMF type',
        PROJECTNAME+'.toolbox',
        'switchATCT2CMF')
    manage_addExternalMethod(self,'switchCMF2ATCT',
        'Set ATCT as default content types',
        PROJECTNAME+'.toolbox',
        'switchCMF2ATCT')

    manage_addExternalMethod(self,'migrateFromCMFtoATCT',
        'Migrate from CMFDefault types to ATContentTypes',
        PROJECTNAME+'.migrateFromCMF',
        'migrate')

    #manage_addExternalMethod(portal,'migrateFromCPTtoATCT',
    #    'Migrate from CMFPloneTypes types to ATContentTypes',
    #    PROJECTNAME+'.migrateFromCPT',
    #    'migrate')

    #manage_addExternalMethod(portal,'recreateATImageScales',
    #    '',
    #    PROJECTNAME+'.toolbox',
    #    'recreateATImageScales')
        
    # changing workflow
    setupWorkflows(self, typeInfo, out)

    # setup content type registry
    old = ('link', 'news', 'document', 'file', 'image')
    setupMimeTypes(self, typeInfo, old=old, moveDown=(IATFile,), out=out)
    registerActionIcons(self, out)
    
    return out.getvalue()

def uninstall(self):
    out = StringIO()
    classes=listTypes(PROJECTNAME)

    # switch back before uninstalling
    #if isSwitchedToATCT(self):
    #    switchATCT2CMF(self)

    # remove external methods for toggling between old and new types
    for script in ('switch_old_plone_types_on', 'switch_old_plone_types_off',
     'migrateFromCMFtoATCT', 'migrateFromCPTtoATCT', 'recreateATImageScales',
     'switchATCT2CMF', 'switchCMF2ATCT', ):
        if hasattr(aq_base(self), script):
            self.manage_delObjects(ids=[script,])

    return out.getvalue()

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
