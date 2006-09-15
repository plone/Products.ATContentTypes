## Script (Python) "getXMLSelectVocab"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=method,param,value
##title=Get a DisplayList and format for XML request

params = {param:value, 'display_list': True}

vocab = getattr(context, method)(**params)

RESPONSE = context.REQUEST.RESPONSE
RESPONSE.setHeader('Content-Type', 'text/xml')

# this is broken (for example: language german + field=review_state)
##results = [(trans(vocab.getMsgId(item), default=vocab.getValue(item)), item)
##                    for item in vocab]

results = [(vocab.getValue(item), item) for item in vocab]

item_strings = ['^'.join(a) for a in results]
result_string = '|'.join(item_strings)

return "<div>%s</div>" % result_string