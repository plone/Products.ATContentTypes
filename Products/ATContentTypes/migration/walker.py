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

import sys
import logging
import traceback
from cStringIO import StringIO

#from Products.ATContentTypes.migration.common import LOG
from Products.ATContentTypes.migration.common import HAS_LINGUA_PLONE
from Products.ATContentTypes.migration.common import registerWalker
from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent
from Products.CMFPlone import transaction

LOG = logging.getLogger('ATCT.migration')

class StopWalking(StopIteration):
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
    
    arguments:
    * portal
      portal root object as context
    * migrator
      migrator class
    * src and dst_portal_type
      ids of the portal types to migrate
    * transaction_size (int)
      Amount of objects before a transaction, subtransaction or new savepoint is
      created. A small number might slow down the process since transactions are
      possible costly.
    * full_transaction
      Commit a full transaction after transaction size
    * use_savepoint
      Create savepoints and roll back to the savepoint if an error occurs
  
    full_transaction and use_savepoint are mutual exclusive. 
    o When the default values (both False) are used a subtransaction is committed. 
      If an error occurs *all* changes are lost. 
    o If full_transaction is enabled a full transaction is committed. If an error
      occurs the migration process stops and all changes sine the last transaction
      are lost.
    o If use_savepoint is set savepoints are used. A savepoint is like a
      subtransaction which can be rolled back. If an errors occurs the transaction
      is rolled back to the last savepoint and the migration goes on. Some objects
      will be left unmigrated.
    
    """

    def __init__(self, portal, migrator, src_portal_type=None, dst_portal_type=None,
                 **kwargs):
        self.portal = portal
        self.migrator = migrator
        if src_portal_type is None:
            self.src_portal_type = self.migrator.src_portal_type
        else:
            self.src_portal_type = src_portal_type
        if dst_portal_type is None:
            self.dst_portal_type = self.migrator.dst_portal_type
        else:
            self.dst_portal_type = dst_portal_type
        self.src_meta_type = self.migrator.src_meta_type
        self.dst_meta_type = self.migrator.dst_meta_type
        
        self.transaction_size = int(kwargs.get('transaction_size', 20))
        self.full_transaction = kwargs.get('full_transaction', False)
        self.use_savepoint = kwargs.get('use_savepoint', False)
        
        if self.full_transaction and self.use_savepoint:
            raise ValueError
        
        self.out = StringIO()
        self.counter = 0
        self.errors = []

    def go(self, **kwargs):
        """runner

        Call it to start the migration
        :return: migration notes
        :rtype: list of strings
        """
        self.migrate(self.walk(), **kwargs)

    __call__ = go

    def walk(self):
        """Walks around and returns all objects which needs migration

        :return: objects (with acquisition wrapper) that needs migration
        :rtype: list of objects
        """
        raise NotImplementedError
 
    def migrate(self, objs, **kwargs):
        """Migrates the objects in the ist objs
        """
        out = self.out
        counter = self.counter
        errors = self.errors
        full_transaction = self.full_transaction
        transaction_size = self.transaction_size
        use_savepoint = self.use_savepoint
        
        src_portal_type = self.src_portal_type
        dst_portal_type = self.dst_portal_type
        
        if use_savepoint:
            savepoint = transaction.savepoint()
        
        for obj in objs:
            msg=('Migrating %s (%s -> %s)' %
                            ('/'.join(obj.getPhysicalPath()),
                             src_portal_type, dst_portal_type, ))
            LOG.debug(msg)
            print >>out, msg
            counter+=1

            migrator = self.migrator(obj,
                                     src_portal_type=src_portal_type,
                                     dst_portal_type=dst_portal_type,
                                     **kwargs)
            
            try:
                # run the migration
                migrator.migrate()
            except ConflictError:
                raise
            except: # except all!
                msg = "Failed migration for object %s (%s -> %s)" %  (
                         '/'.join(obj.getPhysicalPath()), src_portal_type,
                         dst_portal_type )
                # printing exception
                f = StringIO()
                traceback.print_exc(limit=None, file=f)
                tb = f.getvalue()
                
                LOG.error(msg, exc_info = sys.exc_info())
                errors.append({'msg' : msg, 'tb' : tb, 'counter': counter})
                
                if use_savepoint:
                    # Rollback to savepoint
                    LOG.info("Rolling back to last safe point")
                    prin >>out, msg
                    print >>out, tb
                    savepoint.rollback()
                #  stop migration process after an error
                # aborting transaction
                transaction.abort()
                raise MigrationError(obj, migrator, tb)
                
            if counter % transaction_size == 0:
                if full_transaction:
                    transaction.commit()
                    LOG.debug('Transaction comitted after %s objects' % counter)
                elif use_savepoint:
                    LOG.debug('Creating new safepoint after %s objects' % counter)
                    savepoint = transaction.savepoint()
                else:
                    LOG.debug('Committing subtransaction after %s objects' % counter)
                    transaction.commit(1)
        
        self.out = out
        self.counter = counter
        self.errors = errors

    def getOutput(self):
        """Get migration notes

        :return: objects (with acquisition wrapper) that needs migration
        :rtype: list of objects
        """
        return self.out.getvalue()

class CatalogWalker(Walker):
    """Walker using portal_catalog
    """

    def __init__(self, portal, migrator, src_portal_type=None, dst_portal_type=None,
                 **kwargs):
        Walker.__init__(self, portal, migrator, src_portal_type, dst_portal_type,
                        **kwargs)
        self.catalog = getToolByName(portal, 'portal_catalog')

    def walk(self):
        """Walks around and returns all objects which needs migration

        :return: objects (with acquisition wrapper) that needs migration
        :rtype: generator
        """
        catalog = self.catalog
        query = {
            'portal_type' : self.src_portal_type,
            'meta_type' : self.src_meta_type,
        }

        if HAS_LINGUA_PLONE and 'Language' in catalog.indexes():
            #query['Language'] = catalog.uniqueValuesFor('Language')
            query['Language'] = 'all'

        for brain in catalog(query):
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
    
    Requires ExtendedPathIndex!
    """

    def __init__(self, portal, migrator, src_portal_type=None, dst_portal_type=None,
                 depth=1, max_depth=100, **kwargs):
        Walker.__init__(self, portal, migrator, src_portal_type, dst_portal_type,
                        **kwargs)
        self.catalog = getToolByName(portal, 'portal_catalog')    
        self.depth=depth
        self.max_depth = max_depth

    def walk(self):
        """Walks around and returns all objects which needs migration

        :return: objects (with acquisition wrapper) that needs migration
        :rtype: generator
        
        TODO: stop when no objects are left. Don't try to migrate until the walker
              reaches max_depth
        """
        depth = self.depth
        max_depth = self.max_depth
        catalog = self.catalog
        root = '/'.join(self.portal.getPhysicalPath())
        query = {
            'portal_type' : self.src_portal_type,
            'meta_type' : self.src_meta_type,
            'path' : {'query' : root, 'depth' : depth},
        }

        if HAS_LINGUA_PLONE and 'Language' in catalog.indexes():
            #query['Language'] = catalog.uniqueValuesFor('Language')
            query['Language'] = 'all'
                                                        
        while True:
            if depth > max_depth:
                raise StopWalking
            query['path']['depth'] = depth
            for brain in catalog(query):
                obj = brain.getObject()
                try: state = obj._p_changed
                except: state = 0
                if obj is not None:
                    yield obj
                    # safe my butt
                    if state is None: obj._p_deactivate()
            
            depth+=1

registerWalker(CatalogWalkerWithLevel)

def useLevelWalker(portal, migrator, **kwargs):
    w = CatalogWalkerWithLevel(portal, migrator)
    return w.go(**kwargs)

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
