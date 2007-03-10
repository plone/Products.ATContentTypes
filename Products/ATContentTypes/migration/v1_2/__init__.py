"""Migration functions for ATContentTypes 1.2. These are called during the
   usual CMFPlone migration.
"""
import transaction
from zope.component import getUtility
from zope.component import queryUtility

from Acquisition import aq_base
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.interface import IATCTTool
from Products.ATContentTypes.tool.atct import ATCTTool

def upgradeATCTTool(portal, out):
    tool = queryUtility(IATCTTool)
    if not hasattr(aq_base(tool), '_version'):
        # the tool already has been upgraded
        return
    # First we get all relevant old configuration and make sure we get
    # real copies of the various objects
    old_conf = {}
    old_conf['album_batch_size'] = int(tool.album_batch_size)
    old_conf['album_image_scale'] = str(tool.album_image_scale)
    old_conf['image_types'] = list(tool.image_types)
    old_conf['folder_types'] = list(tool.folder_types)
    old_conf['single_image_scale'] = str(tool.single_image_scale)
    old_conf['topic_indexes'] = tool.topic_indexes.copy()
    old_conf['topic_metadata'] = tool.topic_metadata.copy()
    old_conf['allowed_portal_types'] = tuple(tool.allowed_portal_types)
    
    # Remove the old tool completely
    del(tool)
    portal._delObject(TOOLNAME)
    transaction.savepoint(optimistic=True)
    
    # Create new tool
    portal._setObject(TOOLNAME, ATCTTool())
    tool = queryUtility(IATCTTool)
    # And apply the configuration again
    tool._setPropValue('album_batch_size', old_conf['album_batch_size'])
    tool._setPropValue('album_image_scale', old_conf['album_image_scale'])
    tool._setPropValue('image_types', tuple(old_conf['image_types']))
    tool._setPropValue('folder_types', tuple(old_conf['folder_types']))
    tool._setPropValue('single_image_scale', old_conf['single_image_scale'])
    tool._setPropValue('allowed_portal_types', old_conf['allowed_portal_types'])

    # XXX Index and metadata should be updated instead of being reapplied
    tool._setPropValue('topic_indexes', old_conf['topic_indexes'])
    tool._setPropValue('topic_metadata', old_conf['topic_metadata'])

    transaction.savepoint(optimistic=True)
    
    out.append('Upgraded the ATContentTypes tool.')
