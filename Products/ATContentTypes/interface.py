# -*- coding: utf-8 -*-
"""AT Content Types general interfaces

BBB: We used to have all interfaces specified in "interface". "interfaces" is
the conventional name, though.
"""

#     File "<stdin>", line 1, in <module>
#   >>> import Products.ATContentTypes.interface.interfaces
#   ImportError: No module named interfaces
#   Traceback (most recent call last):
# again.  to work around we inject them manually...
# apparently the modules imported from `interfaces` above are already
# seen in plone 4 when trying to import submodules from `ATCT.interface`:
# somehow known to the interpreter and therefore not added to `sys.modules`
# the following is a rather crude workaround for the failing imports
from Products.ATContentTypes.interfaces import *
from sys import modules
from types import ModuleType


for name, obj in globals().items():
    if isinstance(obj, ModuleType):
        modules['%s.%s' % (__name__, name)] = obj
