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
"""ATContentTypes customization policy for Plone sites

Based on the multilingual policy from Plone Solutions
"""
__author__  = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'

from StringIO import StringIO

from Products.CMFPlone.Portal import addPolicy
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.config import TOOLNAME
from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy
from Products.Archetypes.customizationpolicy import ArchetypesSitePolicy
from Products.Archetypes.utils import shasattr

PRODUCTS = ('ATReferenceBrowserWidget', 'ATContentTypes', )

# Check for Plone 2.1
try:
    from Products.CMFPlone.migrations import v2_1
except ImportError:
    HAS_PLONE21 = False
else:
    HAS_PLONE21 = True

class ATCTSitePolicy(ArchetypesSitePolicy):
    """Site policy for SA
    """

    def customize(self, portal):
        out = StringIO()
        oldout = ArchetypesSitePolicy.customize(self, portal)
        print >>out, oldout,
        self.installATCT(portal, out)
        self.setupATCT(portal, out)
        return out.getvalue()
    
    def installATCT(self, portal, out):
        """Install Archetypes with all dependencies
        """
        print >>out, 'Installing ATContentTypes ...'
        qi = getToolByName(portal, 'portal_quickinstaller')
        for product in PRODUCTS:
            if not qi.isProductInstalled(product):
                qi.installProduct(product)
                # Refresh skins
                if shasattr(portal, '_v_skindata'):
                    portal._v_skindata = None
                if shasattr(portal, 'setupCurrentSkin'):
                    portal.setupCurrentSkin()
                print >>out, '   Installed %s' % product
            else:
                print >>out, '   %s already installed' % product
        print >>out, 'Done\n'

    def setupATCT(self, portal, out):
        """
        """
        # migrate content
        print >>out, 'Setting up ATContentTypes ...'
        get_transaction().commit(1)
        tool = getToolByName(portal, TOOLNAME)
        tool.migrateToATCT()
        print >>out, 'Done\n'


    
def registerPolicy(context):
    if not HAS_PLONE21:
        addPolicy('ATContentTypes Site', ATCTSitePolicy())
