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

import datetime
from DateTime import DateTime

def dt2DT(date):
    """Convert Python's datetime to Zope's DateTime
    """
    return DateTime(*date.timetuple()[:6])

def DT2dt(date):
    """Convert Zope's DateTime to Pythons's datetime
    """
    # seconds (parts[6]) is a float, so we map to int
    args = map(int, date.parts()[:6])
    return datetime.datetime(*args)

def toTime(date):
    """get time part of a date
    """
    if isinstance(date, datetime.datetime):
        date = dt2DT(date)
    return date.Time()

def toSeconds(td):
    """Converts a timedelta to an integer representing the number of seconds 
    """
    return td.seconds + td.days * 86400
    
def moveFieldInSchema(schema, fieldName, index, schemata=None):
    """Given a Schema and the name of a field in this schema, move the field 
    within its schemata to the position given by index. For example, giving
    index 0 will move the field to the top of the schema. Negative indexes
    are also permitted: Giving index -1 will move it to the bottom, whilst
    -2 will make the field the second-last in its schemata.
    
    If the 'schemata' argument is given, this gives the name of the schemata
    the field should be placed in. If the field is in another schemata, it will
    be moved.
    
    The method will *not* create a copy of schema before modifying it. If you
    are moving fields from a shared schema (e.g. BaseSchema or BaseMetadata),
    you should create a copy before passing the copy in to this method, to
    avoid modifying *all* instances of that schema. Since the schema is modified
    in-place, the method does not return anything.
    
    May raise KeyError if fieldName cannot be found, IndexError if the index
    is out of range.
    """
    
    field = schema[fieldName]
    
    if schemata is not None:
        field.schemata = schemata
    else:
        schemata = field.schemata
    
    # Code adapted from ManagedSchema.moveField()
    
    fields = schema.fields()
    fieldNames = [f.getName() for f in fields]
    schemataNames = schema.getSchemataNames()

    schemataFields = {}
    for schemataName in schemataNames:
        schemataFields[schemataName] = schema.getSchemataFields(schemataName)

    currentSchemataFields = schemataFields[schemata]
    currentIndex = [f.getName() for f in currentSchemataFields].index(field.getName())

    if index < 0:
        index = len(currentSchemataFields) - (-1 * index)

    # Move the item by deleting it and re-inserting it in the schemata list
    del currentSchemataFields[currentIndex]
    currentSchemataFields.insert(index, field)

    schemataFields[schemata] = currentSchemataFields
    
    # Re-initialise the schema
    schema.__init__()
    for schemataName in schemataNames:
        for f in schemataFields[schemataName]:
            schema.addField(f)