from zope.interface import implements
from zope.interface import Interface

from Products.GenericSetup.interfaces import IFilesystemExporter

# BBB: Leaving this old 'temporary hack' in, in case people are relying on it.
# It's no longer used in core.


class IDisabledExport(Interface):
    pass


class NullExporterAdapter(object):
    """Dummy exporter that does nothing
    """

    implements(IFilesystemExporter)

    def __init__(self, context):
        self.context = context

    def export(self, export_context, subdir):
        pass

    def listExportableItems(self):
        return []
