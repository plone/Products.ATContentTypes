"""Migration tools for ATContentTypes

Migration system for the migration from CMFDefault/Event types to archetypes
based CMFPloneTypes (http://sf.net/projects/collective/).

Copyright (c) 2004, Christian Heimes and contributors
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
 * Neither the name of the author nor the names of its contributors may be used
   to endorse or promote products derived from this software without specific
   prior written permission.


"""

from Products.Archetypes.debug import log as at_log
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
import sys

DEBUG      = False
REMOVE_OLD = True

def LOG(logmessage):
    """ wrap archetypes log method
    """
    if DEBUG:
        at_log(logmessage)

class StdoutStringIO(StringIO):
    """StringIO that also writes to stdout
    """
    
    def write(self, s):
        print >> sys.stdout, str(s),
        StringIO.write(self, s)

## LinguaPlone addon?
try:
    from Products.LinguaPlone.public import registerType
except ImportError:
    HAS_LINGUA_PLONE = False
else:
    HAS_LINGUA_PLONE = True
    del registerType

# This method was coded by me (Tiran) for CMFPlone. I'm maintaining a copy here
# to avoid dependencies on CMFPlone
def _createObjectByType(type_name, container, id, *args, **kw):
    """Create an object without performing security checks
    
    invokeFactory and fti.constructInstance perform some security checks
    before creating the object. Use this function instead if you need to
    skip these checks.
    
    This method uses some code from
    CMFCore.TypesTool.FactoryTypeInformation.constructInstance
    to create the object without security checks.
    """
    id = str(id)
    typesTool = getToolByName(container, 'portal_types')
    fti = typesTool.getTypeInfo(type_name)
    if not fti:
        raise ValueError, 'Invalid type %s' % type_name

    # we have to do it all manually :(
    p = container.manage_addProduct[fti.product]
    m = getattr(p, fti.factory, None)
    if m is None:
        raise ValueError, ('Product factory for %s was invalid' %
                           fti.getId())

    # construct the object
    m(id, *args, **kw)
    ob = container._getOb( id )
    
    return fti._finishConstruction(ob)
