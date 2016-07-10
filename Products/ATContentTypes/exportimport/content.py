# -*- coding: utf-8 -*-
from Products.GenericSetup.interfaces import IFilesystemExporter
from zope.interface import implementer
from zope.interface import Interface


# TODO: This is a temporary hack to allow disabling exporting of some
# content types until all of them support proper exporting


class IDisabledExport(Interface):
    pass


@implementer(IFilesystemExporter)
class NullExporterAdapter(object):
    """Dummy exporter that does nothing
    """

    def __init__(self, context):
        self.context = context

    def export(self, export_context, subdir):
        pass

    def listExportableItems(self):
        return []
