## Script (Python) "isATCTbased"
##title=Formats the history diff
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj

from Products.CMFCore.utils import getToolByInterfaceName

iface = getToolByInterfaceName('Products.CMFPlone.interfaces.IInterfaceTool')

return iface.objectImplements(obj,
           'Products.ATContentTypes.interfaces.IATContentType')
