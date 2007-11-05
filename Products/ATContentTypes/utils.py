#  ATContentTypes http://plone.org/products/atcontenttypes/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2006 AT Content Types development team
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
Some utilities.
"""

import datetime
from DateTime import DateTime

class TimeZone(datetime.tzinfo):
    """Unnamed timezone info"""
    
    def __init__(self, minutes):
        self.minutes = minutes
    
    def utcoffset(self, dt):
        return datetime.timedelta(minutes=self.minutes)
    
    def dst(self, dt):
        return datetime.timedelta(0)
    
    def tzname(self):
        aheadUTC = self.minutes > 0
        if aheadUTC: 
            sign = '+'
            mins = self.minutes * -1
        else:
            sign = '-'
            mins = self.minutes
        wholehours = int(self.minutes / 60.)
        minutesleft = self.minutes % 60
        return """%s%0.2d%0.2d""" % (sign, wholehours, minutesleft)

def dt2DT(date):
    """Convert Python's datetime to Zope's DateTime
    """
    args = (date.year, date.month, date.day, date.hour, date.minute, date.second, date.microsecond, date.tzinfo)
    timezone = args[7].utcoffset(date)
    secs = timezone.seconds
    days = timezone.days
    hours = secs/3600 + days*24
    mod = "+"
    if hours < 0:
        mod = ""
    timezone = "GMT%s%d" % (mod, hours)
    args = list(args[:6])
    args.append(timezone)
    return DateTime(*args)

def DT2dt(date):
    """Convert Zope's DateTime to Pythons's datetime
    """
    # seconds (parts[6]) is a float, so we map to int
    args = map(int, date.parts()[:6])
    args.append(0)
    args.append(TimeZone(int(date.tzoffset()/60)))
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
