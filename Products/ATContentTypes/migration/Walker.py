"""Walkers for Migration suite

Migration system for the migration from CMFDefault/Event types to archetypes
based CMFPloneTypes (http://sf.net/projects/collective/).

Copyright (c) 2004-2005, Christian Heimes <ch@comlounge.net> and contributors
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

from Products.ATContentTypes.migration.common import LOG
from Products.ATContentTypes.migration.common import HAS_LINGUA_PLONE
from Products.ATContentTypes.migration.common import StdoutStringIO
from Products.ATContentTypes.migration.common import registerWalker
import sys
import traceback
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent

class StopWalking(Exception):
    pass

class MigrationError(RuntimeError):
    def __init__(self, obj, migrator, traceback):
        self.src_portal_type = migrator.src_portal_type
        self.dst_portal_type = migrator.dst_portal_type
        self.tb = traceback
        if hasattr(obj, 'absolute_url'):
            self.id = obj.absolute_url(1)
        else:
            self.id = repr(obj)

    def __str__(self):
        return "MigrationError for obj %s (%s -> %s):\n" \
               "%s" % (self.id, self.src_portal_type, self.dst_portal_type, self.tb)

class Walker:
    """Walks through the system and migrates every object it finds
    """

    def __init__(self, migrator, portal):
        self.migrator = migrator
        self.portal = portal
        self.src_portal_type = self.migrator.src_portal_type
        self.dst_portal_type = self.migrator.dst_portal_type
        self.subtransaction = self.migrator.subtransaction
        self.out = []

    def go(self, **kwargs):
        """runner

        Call it to start the migration
        :return: migration notes
        :rtype: list of strings
        """
        self.migrate(self.walk(**kwargs), **kwargs)
        return self.getOutput()

    __call__ = go

    def walk(self, **kwargs):
        """Walks around and returns all objects which needs migration

        :return: objects (with acquisition wrapper) that needs migration
        :rtype: list of objects
        """
        raise NotImplementedError
 
    def migrate(self, objs, **kwargs):
        """Migrates the objects in the ist objs
        """
        for obj in objs:
            msg=('Migrating %s from %s to %s ... ' %
                            ('/'.join(obj.getPhysicalPath()),
                             self.src_portal_type, self.dst_portal_type, ))
            LOG(msg)
            self.out.append(msg)

            migrator = self.migrator(obj, **kwargs)
            try:
                # run the migration
                migrator.migrate()
                #raise ValueError, "MyError"
            except: # except all!
                # aborting transaction
                get_transaction().abort()

                # printing exception
                out = StdoutStringIO()
                traceback.print_exc(limit=None, file=out)
                tb = out.getvalue()

                error = MigrationError(obj, migrator, tb)
                msg = str(error)
                LOG(msg)
                self.out[-1]+=msg
                print msg

                # stop migration process after an error
                # the transaction was already aborted by the migrator itself
                raise MigrationError(obj, migrator, tb)
            else:
                LOG('done')
                self.out[-1]+='done'
            if self.subtransaction and \
              (len(self.out) % self.subtransaction) == 0:
                # submit a subtransaction after every X (default 30)
                # migrated objects to safe your butt
                get_transaction().commit(1)
                LOG('comitted...')

    def getOutput(self):
        """Get migration notes

        :return: objects (with acquisition wrapper) that needs migration
        :rtype: list of objects
        """
        return '\n'.join(self.out)

class CatalogWalker(Walker):
    """Walker using portal_catalog
    """

    def __init__(self, migrator, catalog):
        portal = aq_parent(catalog)
        Walker.__init__(self, migrator, portal)
        self.catalog = catalog

    def walk(self, **kwargs):
        """Walks around and returns all objects which needs migration

        :return: objects (with acquisition wrapper) that needs migration
        :rtype: generator
        """
        LOG("src_portal_type: " + str(self.src_portal_type))
        catalog = self.catalog

        if HAS_LINGUA_PLONE and 'Language' in catalog.indexes():
            # usage of Language is required for LinguaPlone
            brains = catalog(portal_type = self.src_portal_type,
                             Language = catalog.uniqueValuesFor('Language'),
                            )
        else:
            brains = catalog(portal_type = self.src_portal_type)

        for brain in brains:
            obj = brain.getObject()
            try: state = obj._p_changed
            except: state = 0
            if obj is not None:
                yield obj
                # safe my butt
                if state is None: obj._p_deactivate()

registerWalker(CatalogWalker)

class CatalogWalkerWithLevel(Walker):
    """Walker using the catalog but only returning objects for a specific depth
    """
    
    def __init__(self, migrator, catalog, depth=2, max_depth=50):
        portal = aq_parent(catalog)
        Walker.__init__(self, migrator, portal)
        self.catalog = catalog
        self.depth=depth
        self.max_depth = max_depth

    def walk(self, **kwargs):
        """Walks around and returns all objects which needs migration

        :return: objects (with acquisition wrapper) that needs migration
        :rtype: generator
        """
        depth = self.depth
        if depth > self.max_depth:
            LOG("CatalogWalkerWithLeve: depth limit of %s reached. STOPPING"
                 % depth)
            raise StopWalking
        
        LOG("src_portal_type: %s, level %s" % (self.src_portal_type, depth))
        catalog = self.catalog

        if HAS_LINGUA_PLONE and 'Language' in catalog.indexes():
            # usage of Language is required for LinguaPlone
            brains = catalog(portal_type = self.src_portal_type,
                             Language = catalog.uniqueValuesFor('Language'),
                            )
        else:
            brains = catalog(portal_type = self.src_portal_type)
        
        if len(brains) == 0:
            # no objects left, stop iteration
            raise StopWalking

        toConvert = []
        for brain in brains:
            # physical path lenght
            pplen = brain.getPath().count('/')
            if pplen == depth:
                # append brains to a list to avoid some problems with lazy lists
                toConvert.append(brain)

        for brain in toConvert:
            obj = brain.getObject()
            try: state = obj._p_changed
            except: state = 0
            if obj is not None:
                yield obj
                # safe my butt
                if state is None: obj._p_deactivate()
            else:
                LOG("Stale brain found at %s" % brain.getPath())

registerWalker(CatalogWalkerWithLevel)    

def useLevelWalker(context, migrator, out=[], depth=1, **kwargs):
    catalog = getToolByName(context, 'portal_catalog')
    while 1:
        # loop around until we got 'em all :]
        w = CatalogWalkerWithLevel(migrator, catalog, depth)
        try:
            o=w.go(**kwargs)
        except StopWalking:
            out.append(w.getOutput())
            break
        else:
            out.append(o)
            depth+=1
    return out

##class RecursiveWalker(Walker):
##    """Walk recursivly through a directory stucture
##    """
##
##    def __init__(self, migrator, portal, checkMethod):
##        Walker.__init__(self, migrator, portal=portal)
##        self.base=portal
##        self.checkMethod = checkMethod
##        #self.list = []
##
##    def walk(self, **kwargs):
##        """
##        """
##        return self.recurse(self.base)
##
##    def recurse(self, folder):
##        for obj in folder.objectValues():
##            if self.checkMethod(obj):
##                yield obj
##            if obj.isPrincipiaFolderish:
##                self.recurse(obj)
