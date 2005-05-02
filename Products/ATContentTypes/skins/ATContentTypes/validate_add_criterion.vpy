## Script (Python) "validate_add_criterion"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##
request = context.REQUEST
indexId=request.get('field')
criterion_type=request.get('criterion_type')
supported = context.validateAddCriterion(indexId, criterion_type)

atct_tool = context.portal_atct
index_obj = atct_tool.getIndex(indexId)
allowed_criteria = index_obj.criteria

if not supported or criterion_type not in allowed_criteria:
    msg = 'Criterion of type ' +\
          '"%s" not added, it does not work with index "%s".' % (criterion_type, indexId)
    return state.set(status='failure', portal_status_message=msg )
else:
    return state.set(status='success')
