#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2004 AT Content Types development team
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
"""ATCT ZConfig datatypes

$Id: datatype.py,v 1.1.2.1 2005/03/01 18:09:45 tiran Exp $
"""
__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Products.CMFCore import CMFCorePermissions
from AccessControl import Permissions as ZopePermissions
from ZConfig.datatypes import IdentifierConversion

_marker = object()

def _getValueFromModule(module, key):
    var = getattr(module, key, _marker)
    if key is _marker:
        raise ValueError, "%s doesn't have an attribute %s" % (module, key)
    return var

def _getValueFromDottedName(dotted_name):
    parts = dotted_name.split('.')
    module_name = '.'.join(parts[:-1])
    key = parts[-1]
    try:
        module = __import__(module_name, globals(), locals(), [key])
    except ImportError, msg:
        raise ValueError, str(msg)
    return _getValueFromModule(module, key)

def permission_handler(value):
    """Parse a permission
    
    Valid value are:
        cmf.NAME - Products.CMFCore.CMFCorePermissions
        zope.NAME - AccessControl.Permissions
        aDottedName
    """
    if value.startswith('cmf.'):
        permission = _getValueFromModule(CMFCorePermissions, value[4:])
    elif value.startswith('zope.'):
        permission = _getValueFromModule(ZopePermissions, value[5:])
    else:
        permission = _getValueFromDottedName(value)
    if not isinstance(permission, basestring):
        raise ValueError, 'Permission %s is not a string: %s' % (permission,
            type(permission))
    return permission

def identifier_none(value):
    if value == 'None':
        return None
    return IdentifierConversion()(value)
    
def mxtidy_handler(section):
    """
    """
    import pdb; pdb.set_trace()