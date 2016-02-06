# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from DocumentTemplate.DT_Util import html_quote
from Products.Archetypes.atapi import ATHistoryAwareMixin
from Products.ATContentTypes import permission as ATCTPermissions
from Products.ATContentTypes.interfaces import IHistoryAware
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

import difflib


class HistoryAwareMixin(ATHistoryAwareMixin):
    """History aware mixin class

    Shows a unified diff history of the content

    This mixin is using some low level functions of the ZODB to get the last
    transaction states (versions) of the current object. Older histories will
    disapear after packing the database so DO NOT rely on the history
    functionality. It's more a gimmick and nice helper to reviewers and site
    managers.
    """

    implements(IHistoryAware)

    security = ClassSecurityInfo()

    actions = ({
        'id': 'history',
        'name': 'History',
        'action': 'string:${object_url}/atct_history',
        'permissions': (ATCTPermissions.ViewHistory, ),
        'visible': False,
    },
    )

    @security.private
    def getHistorySource(self):
        """get source for HistoryAwareMixin

        Must return a (raw) string
        """
        primary = self.getPrimaryField()
        if primary:
            return primary.getRaw(self)
        else:
            return ''

    @security.protected(View)
    def getLastEditor(self):
        """Returns the user name of the last editor.

        Returns None if no last editor is known.
        """
        histories = list(self.getHistories(1))
        if not histories:
            return None
        user = histories[0][3].split(" ")[-1].strip()
        return user

    @security.protected(ATCTPermissions.ViewHistory)
    def getDocumentComparisons(self, max=10, filterComment=0):
        """Get history as unified diff
        """
        mTool = getToolByName(self, 'portal_membership')

        histories = list(self.getHistories())
        if max > len(histories):
            max = len(histories)

        lst = []

        for revisivon in range(1, max):

            oldObj, oldTime, oldDesc, oldUser = histories[revisivon]
            newObj, newTime, newDesc, newUser = histories[revisivon - 1]

            oldText = oldObj.getHistorySource().split("\n")
            newText = newObj.getHistorySource().split("\n")
            # newUser is a string 'user' or 'folders to acl_users user'
            member = mTool.getMemberById(newUser.split(' ')[-1])

            lines = [
                html_quote(line)
                for line in difflib.unified_diff(oldText, newText)
            ][3:]

            description = newDesc
            if filterComment:
                relativUrl = self.absolute_url(1)
                description = '<br />\n'.join(
                              [line
                               for line in description.split('\n')
                               if line.find(relativUrl) != -1]
                )
            else:
                description.replace('\n', '<br />\n')

            if lines:
                lst.append({
                    'lines': lines,
                    'oldTime': oldTime,
                    'newTime': newTime,
                    'description': description,
                    'user': newUser,
                    'member': member
                })
        return lst

InitializeClass(HistoryAwareMixin)
