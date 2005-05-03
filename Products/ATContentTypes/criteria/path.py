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
""" Topic:

"""

__author__  = 'Alec Mitchell'
__docformat__ = 'restructuredtext'
__old_name__ = 'Products.ATContentTypes.types.criteria.ATPathCriterion'

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import Schema
from Products.Archetypes.public import LinesField, BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget

from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.criteria import PATH_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.permission import ChangeTopics
from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema

from types import StringType

class SiteMapWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro' : "sitemap_widget",
        })
    security = ClassSecurityInfo()

registerWidget(SiteMapWidget,
               title='Selection',
               description=('Renders a plone site map, which '
                            'from which a list of site paths can be selected '
                            'with checkboxes'),
               used_for=('Products.Archetypes.Field.StringField',
                         'Products.Archetypes.Field.LinesField',)
               )

ATPathCriterionSchema = ATBaseCriterionSchema + Schema((
    LinesField('value',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Value",
                mutator="setValue",
                default_method='getCurrentPath',
                widget=SiteMapWidget(
                    label="Folders",
                    label_msgid="label_path_criteria_value",
                    description="Folders to search in.",
                    description_msgid="help_path_criteria_value",
                    i18n_domain="plone"),
                ),
    BooleanField('recurse',
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Recurse",
                default=False,
                widget=BooleanWidget(
                    label="Search Sub-Folders",
                    label_msgid="label_path_criteria_recurse",
                    description="",
                    description_msgid="help_path_criteria_recurse",
                    i18n_domain="plone"),
                ),
    ))

class ATPathCriterion(ATBaseCriterion):
    """A path criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATPathCriterionSchema
    meta_type      = 'ATPathCriterion'
    archetype_name = 'Path Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'portal location'

    def getCurrentPath(self):
        """ Returns the path of the parent object so that we know where we are
            in the sitemap """
        portal = self.portal_url.getPortalObject()
        nav_props = self.portal_properties.navtree_properties
        nav_types = nav_props.getProperty('typesToList', None)
        obj = self
        while getattr(obj,'portal_type', None) not in nav_types and obj != portal:
            try:
                obj = obj.aq_inner.aq_parent
            except AttributeError:
                return ()
        return ('/'.join(obj.getPhysicalPath()),)

    security.declareProtected(CMFCorePermissions.View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []
        depth = (not self.Recurse() and 1) or 0

        if self.Value() is not '':
            result.append((self.Field(), {'query': self.Value(), 'depth': depth}))

        return tuple( result )

registerCriterion(ATPathCriterion, PATH_INDICES)
