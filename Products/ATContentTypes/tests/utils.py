def Xprint(s):
    """print helper

    print data via print is not possible, you have to use
    ZopeTestCase._print or this function
    """
    ZopeTestCase._print(str(s)+'\n')

def dcEdit(obj):
    """dublin core edit (inplace)
    """
    obj.setTitle('Test Title')
    obj.setDescription('Test description')
    # XXX more
    
from Products.validation import ValidationChain
EmptyValidator = ValidationChain('isEmpty')
EmptyValidator.appendSufficient('isEmpty')
idValidator = ValidationChain('isValidId')
idValidator.appendSufficient('isEmptyNoError')
idValidator.appendRequired('isValidId')
TidyHTMLValidator = ValidationChain('isTidyHtmlChain')
#TidyHTMLValidator.appendSufficient('isEmpty')
TidyHTMLValidator.appendRequired('isTidyHtmlWithCleanup')
URLValidator = ValidationChain('isURL')
URLValidator.appendSufficient('isEmptyNoError')
URLValidator.appendRequired('isURL')
RequiredURLValidator = ValidationChain('isRequiredURL')
RequiredURLValidator.appendRequired('isURL')
EmailValidator = ValidationChain('isEmailChain')
EmailValidator.appendSufficient('isEmptyNoError')
EmailValidator.appendRequired('isEmail')
PhoneValidator = ValidationChain('isPhoneChain')
PhoneValidator.appendSufficient('isEmptyNoError')
PhoneValidator.appendRequired('isInternationalPhoneNumber')
