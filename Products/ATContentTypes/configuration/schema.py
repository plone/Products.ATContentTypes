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
#  You should have received a copy of the GNU Gefneral Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""ATCT ZConfig schema loader

"""
__author__  = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'

import os
import sys

from ZConfig.datatypes import Registry
from ZConfig.loader import SchemaLoader
from Products.ATContentTypes.configuration import datatype

# schema file
DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE_NAME = 'schema.xml'
SCHEMA_FILE = os.path.join(DIR, SCHEMA_FILE_NAME)

# registry
# ATCT is using its own datatypes registry to add additional
# handlers.
atctRegistry = Registry()
atctRegistry.register('permission', datatype.permission_handler)
atctRegistry.register('identifer_none', datatype.identifier_none)

# schema
atctSchema = None
def loadSchema(file, registry=atctRegistry, overwrite=False):
    """Loads a schema file
    
    * file
      A path to a file
    * registry
      A ZConfig datatypes registry instance
    * overwrite
      Overwriting the existing global schema is not possible unless overwrite
      is set to true. Useful only for unit testing.
    """
    global atctSchema
    if atctSchema is not None and not overwrite:
        raise RuntimeError, 'Schema is already loaded'
    schemaLoader = SchemaLoader(registry=registry)
    atctSchema = schemaLoader.loadURL(file)
    return atctSchema

loadSchema(SCHEMA_FILE)

__all__ = ('atctSchema',)
