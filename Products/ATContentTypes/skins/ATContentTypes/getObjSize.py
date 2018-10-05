## Script (Python) "getObjSize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None, size=None
##title=

from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import human_readable_size

if obj is None:
    obj = context

# allow arbitrary sizes to be passed through,
# if there is no size, but there is an object
# look up the object, this maintains backwards
# compatibility
if size is None and base_hasattr(obj, 'get_size'):
    size = obj.get_size()

return human_readable_size(size)
