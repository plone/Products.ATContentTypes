from Products.ATContentTypes.interface import IATCTTool
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.CMFCore.utils import getToolByName

class ATCTToolXMLAdapter(XMLAdapterBase):
    """Node in- and exporter for ATCTTool.
    """
    __used_for__ = IATCTTool

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node=self._doc.createElement('atcttool')
        node.appendChild(self._extractSettings())

        self._logger.info('ATCTTool settings exported.')
        return node

    def _importNode(self, node):
        if self.environ.shouldPurge():
            self._purgeSettings()

        self._initSettings(node)
        self._logger.info('ATCTTool settings imported.')

    def _purgeSettings(self):
        self.context.setCMFTypesAreRecataloged()
        self.context.setVersionFromFS()

    def _initSettings(self, node):
        for child in node.childNodes:
            if child.nodeName=='cmftypes_are_recataloged':
                value=self._convertToBoolean(child.getAttribute('value'))
                self.context.setCMFTypesAreRecataloged(value=value)
            if child.nodeName=='atct_tool_version':
                value=child.getAttribute('value')
                if value == 'from_filesystem':
                    self.context.setVersionFromFS()
                else:
                    self.context.setInstanceVersion(value)

    def _extractSettings(self):
        node=self._doc.createElement('cmftypes_are_recataloged')
        node.setAttribute('value', str(bool(self.context.getCMFTypesAreRecataloged())))
        child=self._doc.createElement('atct_tool_version')
        child.setAttribute('value', str(self.context.getVersion()))
        node.appendChild(child)
        return node


def importATCTTool(context):
    """Import ATCT Tool configuration.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_atct')

    importObjects(tool, '', context)

def exportATCTTool(context):
    """Export ATCT Tool configuration.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_atct', None)
    if tool is None:
        logger = context.getLogger("atcttool")
        logger.info("Nothing to export.")
        return

    exportObjects(tool, '', context)
