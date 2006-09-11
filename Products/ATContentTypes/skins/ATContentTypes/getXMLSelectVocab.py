## Script (Python) "getXMLSelectVocab"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=method,param,value
##title=Get a DisplayList and format fot XML request

params = {param:value}

vocab = getattr(context, method)(**params)

RESPONSE = context.REQUEST.RESPONSE
RESPONSE.setHeader('Content-Type', 'text/xml')
trans = context.translate

results = [(trans(vocab.getMsgId(item), default=vocab.getValue(item)),item)
                    for item in vocab]

item_strings = ['^'.join(a) for a in results]
result_string = '|'.join(item_strings)

return "<div>%s</div>"%result_string