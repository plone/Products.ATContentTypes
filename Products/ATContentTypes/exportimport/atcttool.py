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
        # initialize topic tool
        self.context.topic_indexes = {}
        self.context.topic_metadata = {}
        self.context.allowed_portal_types = []
        self.context.createInitialIndexes()
        self.context.createInitialMetadata()

    def _initSettings(self, node):
        for child in node.childNodes:
            if child.nodeName=='atct_tool_version':
                value=child.getAttribute('value')
                if value == 'from_filesystem':
                    self.context.setVersionFromFS()
                else:
                    self.context.setInstanceVersion(value)

            if child.nodeName=='cmftypes_are_recataloged':
                value=self._convertToBoolean(child.getAttribute('value'))
                self.context.setCMFTypesAreRecataloged(value=value)

            if child.nodeName=='topic_indexes':
                for indexNode in child.childNodes:
                    if indexNode.nodeName=='index':
                        name=indexNode.getAttribute('name')
                        description=indexNode.getAttribute('description')
                        enabled=self._convertToBoolean(indexNode.getAttribute('enabled'))
                        friendlyName=indexNode.getAttribute('friendlyName')
                        criteria = []
                        for critNode in indexNode.childNodes:
                            if critNode.nodeName == 'criteria':
                                for textNode in critNode.childNodes:
                                    if textNode.nodeName != '#text' or \
                                        not textNode.nodeValue.strip():
                                        continue
                                    criteria.append(str(textNode.nodeValue))
                    
                        self.context.addIndex(name,
                                              friendlyName=friendlyName,
                                              description=description,
                                              enabled=enabled,
                                              criteria=criteria)
                    
            if child.nodeName=='topic_metadata':
                for metadataNode in child.childNodes:
                    if metadataNode.nodeName=='metadata':
                        name=metadataNode.getAttribute('name')
                        description=metadataNode.getAttribute('description')
                        enabled=self._convertToBoolean(metadataNode.getAttribute('enabled'))
                        friendlyName=metadataNode.getAttribute('friendlyName')
                        self.context.addMetadata(name,
                                                 friendlyName=friendlyName,
                                                 description=description,
                                                 enabled=enabled)

    def _extractSettings(self):
        fragment = self._doc.createDocumentFragment()
        node=self._doc.createElement('atct_tool_version')
        node.setAttribute('value', str(self.context.getVersion()[1]))
        fragment.appendChild(node)
        node=self._doc.createElement('cmftypes_are_recataloged')
        node.setAttribute('value', str(bool(self.context.getCMFTypesAreRecataloged())))
        fragment.appendChild(node)
        # topic tool indexes
        indexes=self._doc.createElement('topic_indexes')
        for indexname in self.context.getIndexes():
            index = self.context.getIndex(indexname)
            child=self._doc.createElement('index')
            child.setAttribute('name', str(indexname))
            child.setAttribute('friendlyName', str(index.friendlyName))
            child.setAttribute('description', str(index.description))
            child.setAttribute('enabled', str(bool(index.enabled)))
            for criteria in index.criteria:
                if criteria != 'criterion':
                    sub = self._doc.createElement('criteria')
                    sub.appendChild(self._doc.createTextNode(criteria))
                    child.appendChild(sub)
            indexes.appendChild(child)
        fragment.appendChild(indexes)
        # topic tool metadata
        metadata=self._doc.createElement('topic_metadata')
        for metaname in self.context.getAllMetadata():
            meta = self.context.getMetadata(metaname)
            child=self._doc.createElement('metadata')
            child.setAttribute('name', str(metaname))
            child.setAttribute('friendlyName', str(meta.friendlyName))
            child.setAttribute('description', str(meta.description))
            child.setAttribute('enabled', str(bool(meta.enabled)))
            metadata.appendChild(child)
        fragment.appendChild(metadata)
        
        return fragment

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
