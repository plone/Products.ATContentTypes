## Script (Python) "atctListAlbum"
##title=Helper method for photo album view
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=images=0, folders=0, subimages=0, others=0

from Products.CMFCore.utils import getToolByName

result = {}

if images:
    result['images'] = context.listFolderContents(contentFilter={'Type':('Image',)})
if folders:
    result['folders'] = context.listFolderContents(contentFilter={'Type':('Folder',)})
if subimages:
    catalog = getToolByName(context, 'portal_catalog')
    path = '/'.join(context.getPhysicalPath())
    result['subimages'] = catalog(portal_type='Image', path=path)
if others:
    allowedContentTypes = context.allowedContentTypes()
    filtered = [type.getId() for type in allowedContentTypes
                if type.getId() not in ('Image', 'Folder',) ]
    if filtered:
        result['others'] = context.listFolderContents(contentFilter={'Type':filtered})
    else:
        result['others'] = ()

return result
