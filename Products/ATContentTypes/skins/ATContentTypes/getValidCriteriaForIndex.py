## Script (Python) "getValidIndexes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=index
##title=Determine whether to show an id in an edit form

results = context.allowedCriteriaForField(index, string_list=True)

RESPONSE = context.REQUEST.RESPONSE
RESPONSE.setHeader('Content-Type', 'text/xml')

item_strings = ['^'.join(a) for a in results]
result_string = '|'.join(item_strings)

print "<div>%s</div>"%result_string

return printed

