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

__author__ = 'Alec Mitchell'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase
from Products.ATContentTypes.tests.utils import dcEdit

from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.public import *

from Products.ATContentTypes.types.ATTopic import ATTopic
from Products.ATContentTypes.types.ATTopic import ATTopicSchema
from Products.ATContentTypes.types.ATTopic import ChangeTopics
from Products.ATContentTypes.migration.ATCTMigrator import TopicMigrator
from Products.CMFTopic.Topic import Topic
from Products.ATContentTypes.tests.utils import EmptyValidator
from Products.ATContentTypes.migration.ATCTMigrator import CRIT_MAP, REV_CRIT_MAP
from Products.ATContentTypes.interfaces import IATTopic
from Interface.Verify import verifyObject

ACQUIRE  = True
LIMIT    = False
COUNT  = '150'
CUSTOM   = True
FIELDS   = ('start','end', 'Creator')

CRITERIA_SETUP = {'Integer Criterion':      #Meta Type
                        ('portal_type',     #Field
                         '10 10',            #Value
                         'min:max'),        #Direction
                  'String Criterion':
                        ('SearchableText',
                         'portal'),
                  'Friendly Date Criterion':
                        ('start',
                         '10',
                         'within_day',       #Operation
                         'ahead'),          #DateRange
                  'List Criterion':
                        ('Subject',
                         "value1\nportal\ntest",
                         'OR'),             #Operator
                  'Sort Criterion':
                        ('getId',
                         False),            #Reversed
                }

def editCMF(obj):
    dcEdit(obj)
    obj.edit(acquireCriteria = ACQUIRE, description = obj.Description())
    for meta in CRITERIA_SETUP.keys():
        CRIT_FIELD = CRITERIA_SETUP[meta][0]
        obj.addCriterion(CRIT_FIELD, meta)
    for crit in obj.listCriteria():
        params = CRITERIA_SETUP[crit.meta_type][1:]
        crit.edit(*params)

def editATCT(obj):
    dcEdit(obj)
    obj.setAcquireCriteria(ACQUIRE)
    obj.setLimitNumber(LIMIT)
    obj.setItemCount(COUNT)
    #obj.setCustomView(CUSTOM)
    #obj.setCustomViewFields(FIELDS)
    for meta in CRITERIA_SETUP.keys():
        AT_META = CRIT_MAP[meta]
        CRIT_FIELD = CRITERIA_SETUP[meta][0]
        obj.addCriterion(CRIT_FIELD, AT_META)
    for crit in obj.listCriteria():
        CRIT_TYPE = crit.meta_type
        OLD_CRIT_TYPE = REV_CRIT_MAP[CRIT_TYPE]
        params = CRITERIA_SETUP[OLD_CRIT_TYPE][1:]
        if CRIT_TYPE not in ['ATSortCriterion','ATSimpleIntCriterion']:
            crit.setValue(params[0])
        if CRIT_TYPE == 'ATFriendlyDateCriteria':
            crit.setOperation(params[1])
            DATE_RANGE = (params[2] == 'ahead' and '+') or '-'
            crit.setDateRange(DATE_RANGE)
        if CRIT_TYPE == 'ATListCriterion':
            crit.setOperator(params[1])
        if CRIT_TYPE == 'ATSimpleIntCriterion':
            value = params[0].split(' ')
            crit.setValue(value[0])
            if len(value) > 1: 
                crit.setValue2(value[1])
            crit.setDirection(params[1])
        if CRIT_TYPE == 'ATSortCriterion':
            crit.setReversed(params[0])

def convert_old_catalog_usage(criteria_items):
    """Convert old style query parameters into records"""
    if len(criteria_items) > 1:
        field = criteria_items[0][0]
        query_val = criteria_items[0][1]
        extra_param = criteria_items[1][1]
        if '_usage' in criteria_items[1][0]:
            usage = extra_param.split(':')
            extra_type = usage[0].strip()
            extra_param = ':'.join(usage[1:]).strip()
        else:
            extra_type = criteria_items[1][0].replace('%s_'%field,'')
        criteria_items = [(field, {'query': query_val, extra_type: extra_param})]
    return tuple(criteria_items)

def convert_old_catalog_query(query):
    """Convert old style query to new record based query"""
    for k,v in query.items():
        q_field = q_type = q_param = None
        if '_usage' in k:
            q_field = k.replace('_usage','')
            usage = v.split(':')
            q_type = usage[0].strip()
            q_param = ':'.join(usage[1:]).strip()
        elif '_operator' in k:
            q_field = k.replace('_operator','')
            q_type = 'operator'
            q_param = v
        if q_field:
            new_val = query[q_field]
            if not isinstance(v, dict):
                new_val = { 'query' : new_val }
            new_val[q_type] = q_param
            query[q_field] = new_val
            del query[k]
    return query

tests = []

class TestSiteATTopic(atcttestcase.ATCTTypeTestCase):

    klass = ATTopic
    portal_type = 'Topic'
    cmf_portal_type = 'CMF Topic'
    cmf_klass = Topic
    title = 'Topic'
    meta_type = 'ATTopic'
    icon = 'topic_icon.gif'

    def test_implementsATTopic(self):
        iface = IATTopic
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_Empty( self ):
        topic = self._ATCT

        query = topic.buildQuery()
        self.assertEquals( query, None )

    def test_Simple( self ):
        topic = self._ATCT

        topic.addCriterion( 'foo', 'ATSimpleStringCriterion' )
        self.failUnless('crit__foo_ATSimpleStringCriterion' in
            topic.objectIds(), topic.objectIds())
        topic.getCriterion( 'foo_ATSimpleStringCriterion' ).setValue( 'bar' )

        query = topic.buildQuery()
        self.assertEquals( len(query), 1 )
        self.assertEquals( query['foo'], 'bar' )

        topic.addCriterion( 'baz', 'ATSimpleIntCriterion' )
        topic.getCriterion( 'baz_ATSimpleIntCriterion' ).setValue( '43' )

        query = topic.buildQuery()
        self.assertEquals( len( query ), 2 )
        self.assertEquals( query[ 'foo' ], 'bar' )
        self.assertEquals( query[ 'baz' ], 43 )

    def test_Nested( self ):
        topic = self._ATCT

        topic.addCriterion( 'foo', 'ATSimpleStringCriterion' )
        self.failUnless('crit__foo_ATSimpleStringCriterion' in
            topic.objectIds(), topic.objectIds())
        topic.getCriterion( 'foo_ATSimpleStringCriterion' ).setValue( 'bar' )

        topic.addSubtopic( 'qux' )
        subtopic = topic.qux

        subtopic.setAcquireCriteria(True)
        
        #Ensure an empty subtopic uses it's parents' queries
        self.failUnlessEqual(subtopic.buildQuery(), topic.buildQuery())

        subtopic.addCriterion( 'baz', 'ATSimpleStringCriterion' )
        self.failUnless('crit__baz_ATSimpleStringCriterion' in
            subtopic.objectIds(), subtopic.objectIds())
        subtopic.getCriterion( 'baz_ATSimpleStringCriterion' ).setValue( 'bam' )

        query = subtopic.buildQuery()
        self.assertEquals( len( query ), 2 )
        self.assertEquals( query['foo'], 'bar' )
        self.assertEquals( query['baz'], 'bam' )

        subtopic.setAcquireCriteria(False)
        query = subtopic.buildQuery()
        self.assertEquals( len( query ), 1 )
        self.assertEquals( query['baz'], 'bam' )

    def test_edit(self):
        old = self._cmf
        new = self._ATCT
        editCMF(old)
        editATCT(new)
        self.failUnless(old.Title() == new.Title(), 'Title mismatch: %s / %s' \
                        % (old.Title(), new.Title()))
        self.failUnless(old.Description() == new.Description(), 'Description mismatch: %s / %s' \
                        % (old.Description(), new.Description()))
        #We only need to test truth '1'=1=True 0=None=False
        self.failUnlessEqual(not old.acquireCriteria, not new.getAcquireCriteria(), 'Acquire Criteria mismatch: %s / %s' \
                        % (old.acquireCriteria, new.getAcquireCriteria()))
        #Test all criteria
        for old_crit in old.listCriteria():
            OLD_META = old_crit.meta_type
            FIELD = old_crit.field or old_crit.index
            NEW_META = CRIT_MAP[OLD_META]
            new_crit = new.getCriterion('%s_%s'%(FIELD, NEW_META))
            self.failUnless(convert_old_catalog_usage(
                        old_crit.getCriteriaItems()) == new_crit.getCriteriaItems(),
                        'Criteria mismatch for criteria %s: %s / %s' \
                            % (NEW_META,
                               convert_old_catalog_usage(old_crit.getCriteriaItems()),
                               new_crit.getCriteriaItems()))
        self.failUnless(convert_old_catalog_query(old.buildQuery()) == new.buildQuery(), 'Build Query mismatch: %s / %s' \
                        % (convert_old_catalog_query(old.buildQuery()), new.buildQuery()))

    def test_migration(self):
        old = self._cmf
        id  = old.getId()

        # edit
        editCMF(old)
        title       = old.Title()
        description = old.Description()
        mod         = old.ModificationDate()
        created     = old.CreationDate()

        acquire = old.acquireCriteria
        criteria_dict = dict([[c.meta_type,
                              convert_old_catalog_usage(c.getCriteriaItems())]
                                for c in old.listCriteria()])
        old_query = convert_old_catalog_query(old.buildQuery())

        # migrated (needs subtransaction to work)
        get_transaction().commit(1)
        m = TopicMigrator(old)
        m(unittest=1)
        
        self.failUnless(id in self.folder.objectIds(), self.folder.objectIds())
        migrated = getattr(self.folder, id)

        self.compareAfterMigration(migrated, mod=mod, created=created)
        self.compareDC(migrated, title=title, description=description)

        #Test the one migrated property
        #We only need to test truth '1'=1=True 0=None=False
        self.failUnlessEqual(not migrated.getAcquireCriteria(), not acquire,
                        'Acquire Criteria mismatch: %s / %s' \
                        % (migrated.getAcquireCriteria(), acquire))
        #Test that the criteria return the same query parameters
        for new_crit in migrated.listCriteria():
            OLD_META = REV_CRIT_MAP[new_crit.meta_type]
            self.failUnless(new_crit.getCriteriaItems() == criteria_dict[OLD_META],
                            'Migration Criteria Mismatch for criteria %s: %s / %s'\
                            % (OLD_META, new_crit.getCriteriaItems(),
                                criteria_dict[OLD_META]))
        #Test that the final Topic query is the same
        self.failUnlessEqual(old_query, migrated.buildQuery(),
                            'Build Query mismatch: %s / %s' % \
                                (old_query, migrated.buildQuery()))
        

tests.append(TestSiteATTopic)

class TestATTopicFields(atcttestcase.ATCTFieldTestCase):

    def afterSetUp(self):
        atcttestcase.ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATTopic)

    def test_acquireCriteriaField(self):
        dummy = self._dummy
        field = dummy.getField('acquireCriteria')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == False, 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 0, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getAcquireCriteria',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setAcquireCriteria',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == CMFCorePermissions.View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ChangeTopics,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'boolean', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, BooleanWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_limitNumberField(self):
        dummy = self._dummy
        field = dummy.getField('limitNumber')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == False, 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 0, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getLimitNumber',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setLimitNumber',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == CMFCorePermissions.View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ChangeTopics,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'boolean', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, BooleanWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_itemCountField(self):
        dummy = self._dummy
        field = dummy.getField('itemCount')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == 0, 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 0, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getItemCount',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setItemCount',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == CMFCorePermissions.View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ChangeTopics,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'integer', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, IntegerWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_customViewField(self):
        # XXX not in the current version
        return
        dummy = self._dummy
        field = dummy.getField('customView')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == False, 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 0, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getCustomView',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setCustomView',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == CMFCorePermissions.View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ChangeTopics,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'boolean', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, BooleanWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_customViewFieldsField(self):
        # XXX not in the current version
        return
        dummy = self._dummy
        field = dummy.getField('customViewFields')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == ('Title',), 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 0, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == 'listMetaDataFields',
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == True,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getCustomViewFields',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setCustomViewFields',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == CMFCorePermissions.View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ChangeTopics,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'lines', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, InAndOutWidget),
                        'Value is %s' % id(field.widget))
#         vocab = field.Vocabulary(dummy)
#         self.failUnless(isinstance(vocab, DisplayList),
#                         'Value is %s' % type(vocab))
#         self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

tests.append(TestATTopicFields)

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        for test in tests:
            suite.addTest(unittest.makeSuite(test))
        return suite
