"""AT Content Types migration suite
"""
#Types migration
import Products.ATContentTypes.migration.walker
import Products.ATContentTypes.migration.migrator
import Products.ATContentTypes.migration.atctmigrator
import Products.ATContentTypes.migration.othermigrator
import Products.ATContentTypes.migration.storage

#Vesrion migration
from Products.ATContentTypes.tool import atct

def executeMigrations():
    from Products.ATContentTypes.migration import v1

def null(portal):
    """ This is a null migration, use it when nothing happens """
    pass

def registerMigrations():
    # so the basic concepts is you put a bunch of migrations in here

    atct.registerUpgradePath('0.2.0-final ',
                             '1.0.0-alpha1 ',
                             null)
    atct.registerUpgradePath('1.0.0-alpha1 ',
                             '1.0.0-alpha2 ',
                             v1.alphas.alpha1_alpha2)
    atct.registerUpgradePath('1.0.0-alpha2 ',
                             '1.0.0-devel (snapshot-2005-07-05)',
                             v1.betas.alpha2_beta1)
    atct.registerUpgradePath('1.0.0-devel (snapshot-2005-07-05)',
                             '1.0.0-rc1',
                             v1.betas.beta1_rc1)
