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

__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interfaces import IATContentType

def setupMimeTypes(self, typeInfo, old=(), moveDown=(), out=None):
    """Setup up and registers mimetype associations

    self - portal object
    typeInfo - a list of type infos
    old - a list of old items that should be removed
    moveDown - a list of interfaces. Types that are implementing this interface
               are moved to the bottom of the list
    out - StringIO instance
    """
    reg = getToolByName(self, 'content_type_registry')

    moveBottom = []
    moveTop = []

    for o in old:
        # remove old
        if reg.getPredicate(o):
            reg.removePredicate(o)

    for t in typeInfo:
        klass       = t['klass']
        portal_type = t['portal_type']

        if not IATContentType.isImplementedByInstancesOf(klass):
            # not a AT ContentType (maybe criterion) - skip
            continue

        # major minor
        for name, mm in getMajorMinorOf(klass):
            if reg.getPredicate(name):
                reg.removePredicate(name)
            reg.addPredicate(name, 'major_minor')
            reg.getPredicate(name).edit(**mm)
            reg.assignTypeName(name, portal_type)
            for iface in moveDown:
                if iface.isImplementedByInstancesOf(klass):
                    moveBottom.append(name)
        # extensions
        name, extlist = getFileExtOf(klass)
        if extlist:
            if reg.getPredicate(name):
                reg.removePredicate(name)
            reg.addPredicate(name, 'extension')
            reg.getPredicate(name).edit(extlist)
            reg.assignTypeName(name, portal_type)
            for iface in moveDown:
                if iface.isImplementedByInstancesOf(klass):
                    moveBottom.append(name)
            else:
                moveTop.append(name)

    # move ATFile to the bottom because ATFile is a fallback
    last = len(reg.listPredicates())-1
    for name in moveBottom:
        reg.reorderPredicate(name, last)

    # move extension based rules to the top
    for name in moveTop:
        reg.reorderPredicate(name, 0)

def fixMimeTypes(self, klass, portal_type):
    reg = getToolByName(self, 'content_type_registry')
    for mm_name, mm in getMajorMinorOf(klass):
        if reg.getPredicate(mm_name):
            reg.assignTypeName(mm_name, portal_type)

    ext_name, ext = getFileExtOf(klass)
    if reg.getPredicate(ext_name):
        reg.assignTypeName(ext_name, portal_type)

def getMajorMinorOf(klass):
    """helper method for setupMimeTypes
    """
    retval = []
    for mt in klass.assocMimetypes:
        ma, mi = mt.split('/')
        if mi == '*':
            mi   = ''
            name = '%s' % ma
        else:
            name = '%s_%s' % (ma, mi)
        retval.append( (name, {'major' : ma, 'minor' : mi}) )
    return retval

def getFileExtOf(klass):
    """helper method for setupMimeTypes
    """
    name = '%s_ext' % klass.meta_type
    return (name, klass.assocFileExt)

def registerTemplates(self, typeInfo, out):
    """Registers templates in the archetypes tool
    """
    for t in typeInfo:
        klass          = t['klass']
        portal_type    = klass.portal_type
        registerTemplatesForClass(self, klass, portal_type)

def registerActionIcons(self, out):
    """Register action icons for Calendar
    """
    aitool = getToolByName(self, 'portal_actionicons')
    action_icons = ({
        'category'  : 'plone',
        'action_id' : 'ics',
        'icon_expr' : 'ical_icon.gif',
        'title'     : 'iCalendar export',
        'priority'  : 0,
        },
        {
        'category'  : 'plone',
        'action_id' : 'vcs',
        'icon_expr' : 'vcal_icon.gif',
        'title'     : 'vCalendar export',
        'priority'  : 0,
        },
        )
    for icon in action_icons:
        info = (icon['category'], icon['action_id'])
        try:
            aitool.addActionIcon(**icon)
        except KeyError:
            print >>out, 'Action icon %s:%s is already defined, reintalling ' \
                        % info
            aitool.removeActionIcon(icon['category'], icon['action_id'])
            aitool.addActionIcon(**icon)
        else:
            print >>out, 'Added action icon %s:%s' % info
