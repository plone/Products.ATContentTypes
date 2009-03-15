from zope.interface import Interface
from zope.interface import Attribute

from Products.Archetypes.interfaces import IBaseContent
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault


class IATContentType(ISelectableBrowserDefault, IBaseContent):
    """Marker interface for AT Content Types
    """

    default_view = Attribute('''Default view template - used for dynamic view''')
    suppl_views = Attribute('''Supplementary views - used for dynamic view''')

    _atct_newTypeFor = Attribute('''XXX''')

    assocMimetypes = Attribute('''A tuple of mimetypes that are associated
                                  with this type. Format: ('bar/foo', 'foo/*',)
                               ''')

    assocFileExt = Attribute('''A tuple of file extensions that are associated
                                with this type. Format: ('jpeg', 'png',)
                             ''')

    cmf_edit_kws = Attribute('''List of keyword names.
    
    If one of this kw names is used with edit() then the cmf_edit method is
    called.
    ''')


class ICalendarSupport(Interface):
    """Calendar import/export
    """


class ITextContent(Interface):
    """Interface for types containing text
    """

    def getText(**kwargs):
        """
        """

    def setText(value, **kwargs):
        """
        """
        
    def CookedBody(stx_level='ignored'):
        """
        """

    def EditableBody():
        """
        """

class IATCTTool(Interface):
    """
    """
 
