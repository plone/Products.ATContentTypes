"""AT Content Types migration suite
"""
#Types migration
import Products.ATContentTypes.migration.walker
import Products.ATContentTypes.migration.migrator
import Products.ATContentTypes.migration.atctmigrator

#Vesrion migration
from Products.ATContentTypes.tool import atct

def executeMigrations():
    import v1

def null(portal):
    """ This is a null migration, use it when nothing happens """
    pass

def registerMigrations():
    # so the basic concepts is you put a bunch of migrations in here

    atct.registerUpgradePath('0.2.0-final ',
                             '1.0.0-devel (CVS/Unreleased)',
                             v1.alphas.zero2_alpha1)