from Products import ATContentTypes as PRODUCT
import os.path

version=PRODUCT.__version__
modname=PRODUCT.__name__

# (major, minor, patchlevel, release info) where release info is:
# -99 for alpha, -49 for beta, -19 for rc and 0 for final
# increment the release info number by one e.g. -98 for alpha2
vers, rest = version.split(' ')
major, minor, bugfix =  vers.split('.')
bugfix, release = bugfix.split('-')

numversion = (int(major), int(minor), int(bugfix), -199)

license     = 'GPL, ZPL'
copyright   = '''(c) 2003-2005 AT Content Types development team'''

author      = 'AT Content Type development team, Christian Heimes <ch@comlounge.net>'
author_email= 'heimes@faho.rwth-aachen.de'

short_desc  = 'Archetypes reimplementation of the CMF core types'
long_desc   = '''
'''

copyright_text = '''XXX
'''

web         = 'http://www.sourceforge.net/projects/collective'
ftp         = ''
mailing_list= 'collective@lists.sourceforge.net'
bugtracker  = 'http://sourceforge.net/tracker/?atid=645337&group_id=55262&func=browse'
