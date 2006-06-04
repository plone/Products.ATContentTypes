#
# Tests for migration components
#

__author__ = 'Alec Mitchell <apm13@columbia.edu>'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.CMFDynamicViewFTI import DynamicViewTypeInformation
from Products.ATContentTypes.tests import atcttestcase
from Products.ATContentTypes.config import TOOLNAME
from Products.CMFCore.utils import getToolByName

from Products.ATContentTypes.migration.v1.alphas import updateDateCriteria
from Products.ATContentTypes.migration.v1.alphas import updateIntegerCriteria
from Products.ATContentTypes.migration.v1.alphas import migrateCMFTopics
from Products.ATContentTypes.migration.v1.alphas import uncatalogCriteria
from Products.ATContentTypes.migration.v1.alphas import addSubTopicAllowed
from Products.ATContentTypes.migration.v1.betas import fixFolderlistingAction
from Products.ATContentTypes.migration.v1.betas import reindexCatalog
from Products.ATContentTypes.migration.v1.betas import addRelatedItemsIndex
from Products.ATContentTypes.migration.v1.betas import renameTopicsConfiglet
from Products.ATContentTypes.migration.v1.betas import removeTopicSyndicationAction
from Products.ATContentTypes.migration.v1.betas import fixViewActions
from Products.ATContentTypes.migration.v1.betas import fixTopicEditAction
from Products.ATContentTypes.migration.v1.betas import removeTopicFolderContentsAction
from Products.ATContentTypes.migration.v1.betas import changeDynView2SelectedLayout
from Products.ATContentTypes.migration.v1.betas import changeSubjectToKeywords
from Products.ATContentTypes.migration.v1.final import removeListCriteriaFromTextIndices
from Products.ATContentTypes.migration.v1.final import fixLocationCriteriaGrammar

from Products.CMFDynamicViewFTI.migrate import migrateFTIs

class MigrationTest(atcttestcase.ATCTSiteTestCase):

    def _createType(self, context, portal_type, id):
        """Helper method to create a new type 
        """
        ttool = getToolByName(context, 'portal_types')
        fti = ttool.getTypeInfo(portal_type)
        fti.constructInstance(context, id)
        return getattr(context.aq_inner.aq_explicit, id)

    def removeActionFromType(self, type_name, action_id):
        # Removes an action from a portal type
        tool = getattr(self.portal, 'portal_types')
        info = tool.getTypeInfo(type_name)
        typeob = getattr(tool, info.getId())
        actions = info.listActions()
        actions = [x for x in actions if x.id != action_id]
        typeob._actions = tuple(actions)

    def addActionToType(self, type_name, action_id, category):
        # Removes an action from a portal type
        tool = getattr(self.portal, 'portal_types')
        info = tool.getTypeInfo(type_name)
        typeob = getattr(tool, info.getId())
        typeob.addAction(action_id, action_id, '', '', '', category)


class TestMigrations_v1(MigrationTest):

    def afterSetUp(self):
        self.setRoles(['Manager', 'Member'])
        self.tool = getToolByName(self.portal, TOOLNAME)
        self.properties = self.portal.portal_properties
        self.catalog = self.portal.portal_catalog
        self.cmf_topic = self._createType(self.folder, 'CMF Topic', 'test_cmftopic')
        self.at_topic = self._createType(self.folder, 'Topic', 'test_attopic')
        self.date_crit = self.at_topic.addCriterion('created','ATFriendlyDateCriteria')
        #Set obselete values to test migration
        self.date_crit.setOperation('min')
        self.date_crit.setDateRange('-')
        self.date_crit.setValue(35)
        #Set only the value parameter
        self.int_crit = self.at_topic.addCriterion('Subject','ATSimpleIntCriterion')
        self.int_crit.setValue(35)
        self.catalog.indexObject(self.int_crit)

# These fail due to lacking subtransactions
#     def testMigrateCMFTopics(self):
#         # Should convert the CMFTopic
#         migrateCMFTopics(self.portal,[])
#         migrated = getattr(self.folder, 'test_cmftopic')
#         self.assertEqual(migrated.portal_type,'Topic')
# 
#     def testMigrateCMFTopicsTwice(self):
#         # Should not fail if migrated again
#         migrateCMFTopics(self.portal,[])
#         migrateCMFTopics(self.portal,[])
#         migrated = getattr(self.folder, 'test_cmftopic')
#         self.assertEqual(migrated.portal_type,'Topic')
# 
#     def testMigrateCMFTopicsNoCatalog(self):
#         # Should not fail if portal_catalog is missing
#         self.portal._delObject('portal_catalog')
#         migrateCMFTopics(self.portal,[])

    def testUncatalogCriteria(self):
        # Should fix our broken date criteria
        self.failUnless(self.catalog(path='/'.join(self.int_crit.getPhysicalPath())))
        uncatalogCriteria(self.portal,[])
        self.failIf(self.catalog(path='/'.join(self.int_crit.getPhysicalPath())))

    def testUncatalogCriteriaTwice(self):
        # Should not fail if migrated again
        uncatalogCriteria(self.portal,[])
        uncatalogCriteria(self.portal,[])
        self.failIf(self.catalog(path='/'.join(self.int_crit.getPhysicalPath())))

    def testUncatalogCriteriaNoCatalog(self):
        # Should not fail if portal_catalog is missing
        self.portal._delObject('portal_catalog')
        uncatalogCriteria(self.portal,[])

    def testUpdateDateCriteria(self):
        # Should fix our broken date criteria
        updateDateCriteria(self.portal,[])
        self.assertEqual(self.date_crit.getOperation(),'less')
        self.assertEqual(self.date_crit.getDateRange(),'-')
        self.assertEqual(self.date_crit.Value(),35)

    def testUpdateDateCriteriaTwice(self):
        # Should not fail if migrated again
        updateDateCriteria(self.portal,[])
        updateDateCriteria(self.portal,[])
        self.assertEqual(self.date_crit.getOperation(),'less')

    def testUpdateDateCriteriaNoCatalog(self):
        # Should not fail if portal_catalog is missing
        self.portal._delObject('portal_catalog')
        updateDateCriteria(self.portal,[])

    def testUpdateIntegerCriteria(self):
        # Should fix our incomplete integer criteria
        # XXX this relies on the current AttributeStorage implementation
        updateIntegerCriteria(self.portal,[])
        self.assertEqual(self.int_crit.value2,None)
        self.assertEqual(self.int_crit.direction,'')
        self.assertEqual(self.int_crit.Value(),35)

    def testUpdateIntegerCriteriaTwice(self):
        # Should not fail if migrated again
        updateIntegerCriteria(self.portal,[])
        updateIntegerCriteria(self.portal,[])

    def testUpdateIntegerCriteriaNoCatalog(self):
        # Should not fail if portal_catalog is missing
        self.portal._delObject('portal_catalog')
        updateIntegerCriteria(self.portal,[])

    def testAddSubTopicAllowed(self):
        ttool = self.portal.portal_types
        topic_fti = ttool.getTypeInfo('Topic')
        topic_fti.manage_changeProperties(allowed_content_types=())
        self.assertEqual(topic_fti.allowed_content_types, ())
        addSubTopicAllowed(self.portal,[])
        self.assertEqual(topic_fti.allowed_content_types, ('Topic',))

    def testAddSubTopicAllowedTwice(self):
        ttool = self.portal.portal_types
        topic_fti = ttool.getTypeInfo('Topic')
        topic_fti.manage_changeProperties(allowed_content_types=())
        addSubTopicAllowed(self.portal,[])
        addSubTopicAllowed(self.portal,[])
        self.assertEqual(topic_fti.allowed_content_types, ('Topic',))

    def testAddSubTopicAllowedNoTool(self):
        self.portal._delObject('portal_types')
        addSubTopicAllowed(self.portal,[])

    def testAddSubTopicAllowedNoFTI(self):
        ttool = self.portal.portal_types
        ttool._delObject('Topic')
        addSubTopicAllowed(self.portal,[])

    def testFixFolderlistingAction(self):
        fixFolderlistingAction(self.portal, [])
        self.failUnless(self.portal.portal_types['Folder'].getActionInfo('folder/folderlisting')['url'].endswith('/view'))
        self.failUnless(self.portal.portal_types['Large Plone Folder'].getActionInfo('folder/folderlisting')['url'].endswith('/view'))
        self.failUnless(self.portal.portal_types['Topic'].getActionInfo('folder/folderlisting')['url'].endswith('/view'))
        
    def testFixFolderlistingActionTwice(self):
        fixFolderlistingAction(self.portal, [])
        self.failUnless(self.portal.portal_types['Folder'].getActionInfo('folder/folderlisting')['url'].endswith('/view'))
        self.failUnless(self.portal.portal_types['Large Plone Folder'].getActionInfo('folder/folderlisting')['url'].endswith('/view'))
        self.failUnless(self.portal.portal_types['Topic'].getActionInfo('folder/folderlisting')['url'].endswith('/view'))
        
    def testFixFolderlistingActionNoTool(self):
        self.portal._delObject('portal_types')
        fixFolderlistingAction(self.portal, [])

    def testAddRelatedItemsIndex(self):
        # Should add getRawRelatedItems index
        self.catalog.delIndex('getRawRelatedItems')
        addRelatedItemsIndex(self.portal, [])
        index = self.catalog._catalog.getIndex('getRawRelatedItems')
        self.assertEqual(index.__class__.__name__, 'KeywordIndex')

    def testAddRelatedItemsIndexTwice(self):
        # Should not fail if migrated again
        self.catalog.delIndex('getRawRelatedItems')
        addRelatedItemsIndex(self.portal, [])
        addRelatedItemsIndex(self.portal, [])
        index = self.catalog._catalog.getIndex('getRawRelatedItems')
        self.assertEqual(index.__class__.__name__, 'KeywordIndex')

    def testAddRelatedItemsIndexNoCatalog(self):
        # Should not fail if portal_catalog is missing
        self.portal._delObject('portal_catalog')
        addRelatedItemsIndex(self.portal, [])

    def testReindexCatalog(self):
        # Should rebuild the catalog
        self.folder.invokeFactory('Document', id='doc', title='Foo')
        self.folder.doc.setTitle('Bar')
        self.assertEqual(len(self.catalog(Title='Foo')), 1)
        reindexCatalog(self.portal, [])
        self.assertEqual(len(self.catalog(Title='Foo')), 0)
        self.assertEqual(len(self.catalog(Title='Bar')), 1)

    def testRenameTopicsConfiglet(self):
        # Should rename the Topics Configlet
        tool = getToolByName(self.portal, TOOLNAME, None)
        cp = getToolByName(self.portal, 'portal_controlpanel', None)
        configlets = tool.getConfiglets()
        topic_configlet = [c for c in configlets if c['name'] == 'Smart Folder Settings'][0]
        topic_configlet = topic_configlet.copy()
        topic_configlet['name'] = 'Old Name'
        cp.unregisterConfiglet(topic_configlet['id'])
        cp.registerConfiglets((topic_configlet,))
        cp_action = [a for a in cp.listActions() if a.id == TOOLNAME][0]
        self.assertEqual(cp_action.title, 'Old Name')
        renameTopicsConfiglet(self.portal, [])
        cp_action = [a for a in cp.listActions() if a.id == TOOLNAME][0]
        self.assertEqual(cp_action.title, 'Smart Folder Settings')

    def testRenameTopicsConfigletTwice(self):
        # Should not fail if migrated again
        cp = getToolByName(self.portal, 'portal_controlpanel', None)
        renameTopicsConfiglet(self.portal, [])
        renameTopicsConfiglet(self.portal, [])
        cp_action = [a for a in cp.listActions() if a.id == TOOLNAME][0]
        self.assertEqual(cp_action.title, 'Smart Folder Settings')

    def testRenameTopicsConfigletNoTool(self):
        # Should not fail if portal_atct is missing
        self.portal._delObject('portal_atct')
        renameTopicsConfiglet(self.portal, [])

    def testRenameTopicsConfigletNoCP(self):
        # # Should not fail if portal_controlpanel is missing
        self.portal._delObject('portal_controlpanel')
        renameTopicsConfiglet(self.portal, [])

    def testReindexCatalog(self):
        # Should rebuild the catalog
        self.folder.invokeFactory('Document', id='doc', title='Foo')
        self.folder.doc.setTitle('Bar')
        self.assertEqual(len(self.catalog(Title='Foo')), 1)
        reindexCatalog(self.portal, [])
        self.assertEqual(len(self.catalog(Title='Foo')), 0)
        self.assertEqual(len(self.catalog(Title='Bar')), 1)

    def testRemoveTopicsSyndicationAction(self):
        # Should remove the syndication action to Topics
        typesTool = getToolByName(self.portal, 'portal_types', None)
        self.addActionToType('Topic', 'syndication', 'object')
        self.failUnless('syndication' in [x.id for x in
                                        typesTool.Topic.listActions()])
        removeTopicSyndicationAction(self.portal, [])
        self.failIf('syndication' in [x.id for x in
                                        typesTool.Topic.listActions()])

    def testRemoveTopicSyndicationActionTwice(self):
        # Should not fail if migrated again
        typesTool = getToolByName(self.portal, 'portal_types', None)
        self.addActionToType('Topic', 'syndication', 'object')
        self.failUnless('syndication' in [x.id for x in
                                        typesTool.Topic.listActions()])
        ret1 = removeTopicSyndicationAction(self.portal, [])
        ret2 = removeTopicSyndicationAction(self.portal, [])
        self.failIf('syndication' in [x.id for x in
                                        typesTool.Topic.listActions()])

    def testAddTopicSyndicationActionNoTool(self):
        # Should not fail if portal_types is missing
        self.portal._delObject('portal_types')
        removeTopicSyndicationAction(self.portal, [])

    def testAddTopicSyndicationActionTypeMissing(self):
        # Should not fail if Topic type is missing
        typesTool = getToolByName(self.portal, 'portal_types', None)
        self.portal.portal_types._delObject('Topic')
        removeTopicSyndicationAction(self.portal, [])

    def testFixViewActions(self):
        fixViewActions(self.portal, [])
        for t in ('Document', 'Event', 'Favorite', 'Link', 'News Item'):
            fti = getattr(self.portal.portal_types, t)
            for a in fti.listActions():
                if a.getId() == 'view':
                    self.assertEqual(a.getActionExpression(), 'string:${object_url}')

    def testFixViewActionsNoTool(self):
        self.portal._delObject('portal_types')
        fixViewActions(self.portal, [])

    def testFixViewActionNoType(self):
        self.portal.portal_types._delObject('Document')
        fixViewActions(self.portal, [])
        for t in ('Event', 'Favorite', 'Link', 'News Item'):
            fti = getattr(self.portal.portal_types, t)
            for a in fti.listActions():
                if a.getId() == 'view':
                    self.assertEqual(a.getActionExpression(), 'string:${object_url}')

    def testFixViewActionsTwice(self):
        fixViewActions(self.portal, [])
        fixViewActions(self.portal, [])
        for t in ('Document', 'Favorite', 'Link', 'News Item'):
            fti = getattr(self.portal.portal_types, t)
            for a in fti.listActions():
                if a.getId() == 'view':
                    self.assertEqual(a.getActionExpression(), 'string:${object_url}')

    def testFixViewActionNoType(self):
        self.portal.portal_types._delObject('Document')
        migrateFTIs(self.portal, product="ATContentTypes")
        for t in ('Event', 'Favorite', 'Link', 'News Item'):
            fti = getattr(self.portal.portal_types, t)
            self.assertEqual(fti.meta_type, DynamicViewTypeInformation.meta_type)

    def testFixViewActionsTwice(self):
        migrateFTIs(self.portal, product="ATContentTypes")
        migrateFTIs(self.portal, product="ATContentTypes")
        for t in ('Document', 'Favorite', 'Link', 'News Item'):
            fti = getattr(self.portal.portal_types, t)
            self.assertEqual(fti.meta_type, DynamicViewTypeInformation.meta_type)

    def testRemoveTopicFolderContentsAction(self):
        # Should remove folder contents action from Topics
        typesTool = getToolByName(self.portal, 'portal_types', None)
        self.addActionToType('Topic', 'folderContents', 'object')
        self.failUnless('folderContents' in [x.id for x in
                                        typesTool.Topic.listActions()])
        ret1 = removeTopicFolderContentsAction(self.portal, [])
        self.failIf(len([x.id for x in typesTool.Topic.listActions()
                                        if x.id == 'folderContents']))

    def testRemoveTopicFolderContentsActionTwice(self):
        # Should not fail if migrated again
        typesTool = getToolByName(self.portal, 'portal_types', None)
        self.addActionToType('Topic', 'folderContents', 'object')
        self.failUnless('folderContents' in [x.id for x in
                                        typesTool.Topic.listActions()])
        ret1 = removeTopicFolderContentsAction(self.portal, [])
        ret2 = removeTopicFolderContentsAction(self.portal, [])
        self.failIf(len([x.id for x in typesTool.Topic.listActions()
                                        if x.id == 'folderContents']))

    def testRemoveTopicFolderContentsActionNoTool(self):
        # Should not fail if portal_types is missing
        self.portal._delObject('portal_types')
        removeTopicFolderContentsAction(self.portal, [])

    def testRemoveTopicFolderContentsActionTypeMissing(self):
        # Should not fail if Topic type is missing
        typesTool = getToolByName(self.portal, 'portal_types', None)
        self.portal.portal_types._delObject('Topic')
        removeTopicFolderContentsAction(self.portal, [])
        
    def test_changeDynView2SelectedLayout(self):
        typesTool = getToolByName(self.portal, 'portal_types', None)
        fti = typesTool['Document']
        # set view aliases to old value
        aliases = fti.getMethodAliases()
        aliases['view'] = '(dynamic view)'
        fti.setMethodAliases(aliases)
        # migrate
        changeDynView2SelectedLayout(self.portal, [])
        # test new value
        aliases = fti.getMethodAliases()
        self.failUnlessEqual(aliases['view'], '(selected layout)')

    def testFixTopicEditAction(self):
        fti = getattr(self.portal.portal_types, 'Topic')
        for a in fti.listActions():
            if a.getId() == 'edit':
                a.setActionExpression('string:${object_url}/atct_edit')
        fixTopicEditAction(self.portal, [])
        for a in fti.listActions():
            if a.getId() == 'edit':
                self.assertEqual(a.getActionExpression(), 'string:${object_url}/edit')

    def testFixTopicEditActionNoTool(self):
        self.portal._delObject('portal_types')
        fixTopicEditAction(self.portal, [])

    def testFixTopicEditActionNoType(self):
        self.portal.portal_types._delObject('Topic')
        fixTopicEditAction(self.portal, [])

    def testFixTopicEditActionTwice(self):
        fti = getattr(self.portal.portal_types, 'Topic')
        for a in fti.listActions():
            if a.getId() == 'edit':
                a.setActionExpression('string:${object_url}/atct_edit')
        fixTopicEditAction(self.portal, [])
        fixTopicEditAction(self.portal, [])
        for a in fti.listActions():
            if a.getId() == 'edit':
                self.assertEqual(a.getActionExpression(), 'string:${object_url}/edit')\

    def testChangeSubjectToKeywords(self):
        tool = self.portal.portal_atct
        tool.updateIndex('Subject','')
        tool.updateMetadata('Subject','')
        self.assertEqual(tool.getIndex('Subject').friendlyName,'')
        self.assertEqual(tool.getMetadata('Subject').friendlyName,'')
        changeSubjectToKeywords(self.portal, [])
        self.assertEqual(tool.getIndex('Subject').friendlyName,'Keywords')
        self.assertEqual(tool.getMetadata('Subject').friendlyName,'Keywords')

    def testChangeSubjectToKeywordsTwice(self):
        tool = self.portal.portal_atct
        tool.updateIndex('Subject','')
        tool.updateMetadata('Subject','')
        changeSubjectToKeywords(self.portal, [])
        changeSubjectToKeywords(self.portal, [])
        self.assertEqual(tool.getIndex('Subject').friendlyName,'Keywords')
        self.assertEqual(tool.getMetadata('Subject').friendlyName,'Keywords')

    def testChangeSubjectToKeywordsNoTool(self):
        self.portal._delOb('portal_atct')
        changeSubjectToKeywords(self.portal, [])

    def testRemoveListCriteriaFromTextIndices(self):
        tool = self.portal.portal_atct
        tool.updateIndex('Subject',
                      criteria=('ATListCriterion', 'ATSimpleStringCriterion'))
        self.failUnless('ATListCriterion' in tool.getIndex('Subject').criteria)
        removeListCriteriaFromTextIndices(self.portal, [])
        self.assertEqual(len(tool.getIndex('Subject').criteria), 1)
        self.failIf('ATListCriterion' in tool.getIndex('Subject').criteria)

    def testRemoveListCriteriaFromTextIndicesTwice(self):
        tool = self.portal.portal_atct
        tool.updateIndex('Subject',
                      criteria=('ATListCriterion', 'ATSimpleStringCriterion'))
        self.failUnless('ATListCriterion' in tool.getIndex('Subject').criteria)
        removeListCriteriaFromTextIndices(self.portal, [])
        removeListCriteriaFromTextIndices(self.portal, [])
        self.assertEqual(len(tool.getIndex('Subject').criteria), 1)
        self.failIf('ATListCriterion' in tool.getIndex('Subject').criteria)

    def testRemoveListCriteriaFromTextIndicesNoTool(self):
        self.portal._delOb('portal_atct')
        removeListCriteriaFromTextIndices(self.portal, [])

    def testFixLocationCriteriaGrammar(self):
        tool = self.portal.portal_atct
        # Break grammar
        tool.updateIndex('path','The location an item in the portal (path)')
        fixLocationCriteriaGrammar(self.portal, [])
        self.assertEqual(tool.getIndex('path').friendlyName, 'The location of an item in the portal (path)')

    def testFixLocationCriteriaGrammarTwice(self):
        tool = self.portal.portal_atct
        # Break grammar
        tool.updateIndex('path','The location an item in the portal (path)')
        fixLocationCriteriaGrammar(self.portal, [])
        fixLocationCriteriaGrammar(self.portal, [])
        self.assertEqual(tool.getIndex('path').friendlyName, 'The location of an item in the portal (path)')

    def testFixLocationCriteriaGrammarNoTool(self):
        self.portal._delOb('portal_atct')
        fixLocationCriteriaGrammar(self.portal, [])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigrations_v1))
    return suite

if __name__ == '__main__':
    framework()
