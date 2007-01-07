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


"""
__author__  = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'
__old_name__ = 'Products.ATContentTypes.types.ATEvent'

from types import StringType

from Products.CMFCore.permissions import ModifyPortalContent, View
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from ComputedAttribute import ComputedAttribute

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import CalendarWidget
from Products.Archetypes.atapi import LinesWidget
from Products.Archetypes.atapi import KeywordWidget
from Products.Archetypes.atapi import RichWidget
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import RFC822Marshaller
from Products.Archetypes.atapi import AnnotationStorage

from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.interfaces import IATEvent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.lib.calendarsupport import CalendarSupportMixin
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.permission import ChangeEvents
from Products.ATContentTypes.utils import DT2dt

from Products.CMFPlone import PloneMessageFactory as _

ATEventSchema = ATContentTypeSchema.copy() + Schema((
    DateTimeField('startDate',
                  required=True,
                  searchable=False,
                  accessor='start',
                  write_permission = ChangeEvents,
                  default_method=DateTime,
                  languageIndependent=True,
                  widget = CalendarWidget(
                        description= '',
                        label=_(u'label_event_start', default=u'Event Starts')
                        )),

    DateTimeField('endDate',
                  required=True,
                  searchable=False,
                  accessor='end',
                  write_permission = ChangeEvents,
                  default_method=DateTime,
                  languageIndependent=True,
                  widget = CalendarWidget(
                        description = '',
                        label = _(u'label_event_end', default=u'Event Ends')
                        )),
    StringField('location',
                searchable=True,
                write_permission = ChangeEvents,
                widget = StringWidget(
                    description = '',
                    label = _(u'label_event_location', default=u'Event Location')
                    )),
    TextField('text',
              required=False,
              searchable=True,
              primary=True,
              storage = AnnotationStorage(migrate=True),
              validators = ('isTidyHtmlWithCleanup',),
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                        description = '',
                        label = _(u'label_event_announcement', default=u'Event body text'),
                        rows = 25,
                        allow_file_upload = zconf.ATDocument.allow_document_upload)),

    LinesField('attendees',
               languageIndependent=True,
               searchable=True,
               write_permission=ChangeEvents,
               widget=LinesWidget(
                      description='',
                      label=_(u'label_event_attendees', default=u'Attendees')
                      )),

    LinesField('eventType',
               required=False,
               searchable=True,
               write_permission = ChangeEvents,
               languageIndependent=True,
               widget = KeywordWidget(
                        size = 6,
                        description='',
                        label = _(u'label_event_type', default=u'Event Type(s)')
                        )),

    StringField('eventUrl',
                required=False,
                searchable=True,
                accessor='event_url',
                write_permission = ChangeEvents,
                widget = StringWidget(
                        description = _(u'help_url',
                                        default=u"Web address with more info about the event. "
                                                 "Add http:// for external links."),
                        label = _(u'label_url', default=u'Event URL')
                        )),

    StringField('contactName',
                required=False,
                searchable=True,
                accessor='contact_name',
                write_permission = ChangeEvents,
                widget = StringWidget(
                        description = '',
                        label = _(u'label_contact_name', default=u'Contact Name')
                        )),

    StringField('contactEmail',
                required=False,
                searchable=True,
                accessor='contact_email',
                write_permission = ChangeEvents,
                validators = ('isEmail',),
                widget = StringWidget(
                        description = '',
                        label = _(u'label_contact_email', default=u'Contact E-mail')
                        )),
    StringField('contactPhone',
                required=False,
                searchable=True,
                accessor='contact_phone',
                write_permission = ChangeEvents,
                validators= (),
                widget = StringWidget(
                        description = '',
                        label = _(u'label_contact_phone', default=u'Contact Phone')
                        )),
    ), marshall = RFC822Marshaller()
    )
finalizeATCTSchema(ATEventSchema)

class ATEvent(ATCTContent, CalendarSupportMixin, HistoryAwareMixin):
    """Information about an upcoming event, which can be displayed in the calendar."""

    schema         =  ATEventSchema

    portal_type    = 'Event'
    archetype_name = 'Event'
    _atct_newTypeFor = {'portal_type' : 'CMF Event', 'meta_type' : 'CMF Event'}
    assocMimetypes = ()
    assocFileExt   = ('event', )
    cmf_edit_kws   = ('effectiveDay', 'effectiveMo', 'effectiveYear',
                      'expirationDay', 'expirationMo', 'expirationYear',
                      'start_time', 'startAMPM', 'stop_time', 'stopAMPM',
                      'start_date', 'end_date', 'contact_name', 'contact_email',
                      'contact_phone', 'event_url')

    __implements__ = (ATCTContent.__implements__, IATEvent,
                      CalendarSupportMixin.__implements__,
                      HistoryAwareMixin.__implements__)

    security       = ClassSecurityInfo()

    security.declareProtected(ChangeEvents, 'setEventType')
    def setEventType(self, value, alreadySet=False, **kw):
        """CMF compatibility method

        Changing the event type changes also the subject.
        """
        if type(value) is StringType:
            value = (value,)
        elif not value:
            # mostly harmless?
            value = ()
        f = self.getField('eventType')
        f.set(self, value, **kw) # set is ok
        if not alreadySet:
            self.setSubject(value, alreadySet=True, **kw)

    security.declareProtected(ModifyPortalContent, 'setSubject')
    def setSubject(self, value, alreadySet=False, **kw):
        """CMF compatibility method

        Changing the subject changes also the event type.
        """
        f = self.getField('subject')
        f.set(self, value, **kw) # set is ok

        # set the event type to the first subject
        if type(value) is StringType:
            v = (value, )
        elif value:
            v = value
        else:
            v = ()

        if not alreadySet:
            self.setEventType(v, alreadySet=True, **kw)

    security.declareProtected(View, 'getEventTypes')
    def getEventTypes(self):
        """fetch a list of the available event types from the vocabulary
        """
        f = self.getField('eventType')
        result = self.collectKeywords('eventType', f.accessor)
        return tuple(result)

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, title=None, description=None, eventType=None,
             effectiveDay=None, effectiveMo=None, effectiveYear=None,
             expirationDay=None, expirationMo=None, expirationYear=None,
             start_date=None, start_time=None, startAMPM=None,
             end_date=None, stop_time=None, stopAMPM=None,
             location=None,
             contact_name=None, contact_email=None, contact_phone=None,
             event_url=None):

        if effectiveDay and effectiveMo and effectiveYear and start_time:
            sdate = '%s-%s-%s %s %s' % (effectiveDay, effectiveMo, effectiveYear,
                                         start_time, startAMPM)
        elif start_date:
            if not start_time:
                start_time = '00:00:00'
            sdate = '%s %s' % (start_date, start_time)
        else:
            sdate = None

        if expirationDay and expirationMo and expirationYear and stop_time:
            edate = '%s-%s-%s %s %s' % (expirationDay, expirationMo,
                                        expirationYear, stop_time, stopAMPM)
        elif end_date:
            if not stop_time:
                stop_time = '00:00:00'
            edate = '%s %s' % (end_date, stop_time)
        else:
            edate = None

        if sdate and edate:
            if edate < sdate:
                edate = sdate
            self.setStartDate(sdate)
            self.setEndDate(edate)

        self.update(title=title, description=description, eventType=eventType,
                    location=location, contactName=contact_name,
                    contactEmail=contact_email, contactPhone=contact_phone,
                    eventUrl=event_url)

    security.declareProtected(View, 'post_validate')
    def post_validate(self, REQUEST=None, errors=None):
        """Validates start and end date

        End date must be after start date
        """
        rstartDate = REQUEST.get('startDate', None)
        rendDate = REQUEST.get('endDate', None)

        if rendDate:
            end = DateTime(rendDate)
        else:
            end = self.end()
        if rstartDate:
            start = DateTime(rstartDate)
        else:
            start = self.start()

        if start > end:
            errors['endDate'] = "End date must be after start date"

    def _start_date(self):
        value = self['startDate']
        if value is None:
            value = self['creation_date']
        return DT2dt(value)

    security.declareProtected(View, 'start_date')
    start_date = ComputedAttribute(_start_date)

    def _end_date(self):
        value = self['endDate']
        if value is None:
            return self.start_date
        return DT2dt(value)

    security.declareProtected(View, 'end_date')
    end_date = ComputedAttribute(_end_date)

    def _duration(self):
        return self.end_date - self.start_date

    security.declareProtected(View, 'duration')
    duration = ComputedAttribute(_duration)

    def __cmp__(self, other):
        """Compare method

        If other is based on ATEvent, compare start, duration and title.
        #If other is a number, compare duration and number
        If other is a DateTime instance, compare start date with date
        In all other cases there is no specific order
        """
        if IATEvent.isImplementedBy(other):
            return cmp((self.start_date, self.duration, self.Title()),
                       (other.start_date, other.duration, other.Title()))
        #elif isinstance(other, (int, long, float)):
        #    return cmp(self.duration, other)
        elif isinstance(other, DateTime):
            return cmp(self.start(), other)
        else:
            # TODO come up with a nice cmp for types
            return cmp(self.Title(), other)

    def __hash__(self):
        return hash((self.start_date, self.duration, self.title))

    security.declareProtected(ModifyPortalContent, 'update')
    def update(self, event=None, **kwargs):
        # Clashes with BaseObject.update, so
        # we handle gracefully
        info = {}
        if event is not None:
            for field in event.Schema().fields():
                info[field.getName()] = event[field.getName()]
        elif kwargs:
            info = kwargs
        ATCTContent.update(self, **info)

registerATCT(ATEvent, PROJECTNAME)
