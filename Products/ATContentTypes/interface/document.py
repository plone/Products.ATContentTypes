#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2005 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from zope.interface import Interface

class IArchiveAccumulator(Interface):
    def initIO():
        """
        reinit the Zip IO
        """

    def setFile(filename,data):
        """
        store the file inside the zip file
        """

    def close():
        """
        close the zip file
        """

    def getRaw():
        """
        return the raw archive
        """

class IFilterFolder(Interface):
    def listObjects():
        """
        """


class IArchiver(Interface):
    def getRawArchive(accumulator=None, **kwargs):
        """
        """

    def createArchive(path, accumulator, **kwargs):
        """
        """

class IDataExtractor(Interface):
    def getData(**kwargs):
        """
        """

class IPhotoAlbum(Interface):
    """
    interface that adapts a folder into a photo album
    """
    def setSymbolicPhoto(photo=None):
        """
        set the photo which represents the album
        """

    def getSymbolicPhoto():
        """
        get the photo which represents the album
        """


class IPhotoAlbumAble(Interface):
    """
    marker interface for possible photoalbum object
    """

class IArchivable(Interface):
    """
    marker interface for possible zippable object
    """
