from Products.ATContentTypes.browser.folder import FolderListingView


class TopicListingView(FolderListingView):

    def folderContents(self):
        limit_display = int(self.request.get('limit_display', 100))
        contents = self.context.queryCatalog(batch=True)
        if len(contents) > limit_display:
            contents = contents[:limit_display]
        return contents
