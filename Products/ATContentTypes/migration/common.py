"""Migration tools for ATContentTypes

Migration system for the migration from CMFDefault/Event types to archetypes
based CMFPloneTypes (http://sf.net/projects/collective/).

Copyright (c) 2004, Christian Heimes <ch@comlounge.net> and contributors
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
__author__  = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'

import sys
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

from Acquisition import aq_base, aq_inner, aq_parent
from App.Dialogs import MessageDialog
from OFS.CopySupport import CopyContainer
from OFS.CopySupport import CopyError
from OFS.CopySupport import eNotSupported
from cgi import escape
import sys

def unrestricted_rename(self, id, new_id):
    """Rename a particular sub-object
    
    Copied from OFS.CopySupport
    
    Less strict version of manage_renameObject:
        * no write look check
        * no verify object check from PortalFolder so it's allowed to rename
          even unallowed portal types inside a folder
    """
    try: self._checkId(new_id)
    except: raise CopyError, MessageDialog(
                  title='Invalid Id',
                  message=sys.exc_info()[1],
                  action ='manage_main')
    ob=self._getOb(id)
    #!#if ob.wl_isLocked():
    #!#    raise ResourceLockedError, 'Object "%s" is locked via WebDAV' % ob.getId()
    if not ob.cb_isMoveable():
        raise CopyError, eNotSupported % escape(id)
    #!#self._verifyObjectPaste(ob)
    #!#CopyContainer._verifyObjectPaste(self, ob)
    try:    ob._notifyOfCopyTo(self, op=1)
    except: raise CopyError, MessageDialog(
                  title='Rename Error',
                  message=sys.exc_info()[1],
                  action ='manage_main')
    self._delObject(id)
    ob = aq_base(ob)
    ob._setId(new_id)

    # Note - because a rename always keeps the same context, we
    # can just leave the ownership info unchanged.
    self._setObject(new_id, ob, set_owner=0)
    ob = self._getOb(new_id)
    ob._postCopy(self, op=1)

    #!#if REQUEST is not None:
    #!#    return self.manage_main(self, REQUEST, update_menu=1)
    return None

class Registry(dict):
    """Common registry
    """
    
    def register(self, cls):
        self[cls.__name__] = cls

class MigratorRegistry(Registry):
    """Migrator Registry
    """
    
    def registerATCT(self, cls, for_cls):
        """Special register method for ATCT based migrators
        """
        cls.src_portal_type = for_cls._atct_newTypeFor['portal_type']
        cls.src_meta_type = for_cls._atct_newTypeFor['meta_type']
        cls.dst_portal_type = for_cls.portal_type
        cls.dst_meta_type = for_cls.meta_type
        self.register(cls)

class WalkerRegistry(Registry):
    """Walker Registry
    """
    pass

_migratorRegistry = MigratorRegistry()
registerMigrator = _migratorRegistry.register
registerATCTMigrator = _migratorRegistry.registerATCT
listMigrators = _migratorRegistry.items

_walkerRegistry = WalkerRegistry()
registerWalker = _walkerRegistry.register
listWalkers = _walkerRegistry.items
