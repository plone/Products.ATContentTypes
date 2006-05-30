"""at Content Types migration suite
"""
#Types migration
import Products.ATContentTypes.migration.walker
import Products.ATContentTypes.migration.migrator
import Products.ATContentTypes.migration.atctmigrator
import Products.ATContentTypes.migration.othermigrator
import Products.ATContentTypes.migration.storage

# Version migration
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
    atct.registerUpgradePath('1.0.0-rc1',
                             '1.0.0-rc2',
                             null)
    atct.registerUpgradePath('1.0.0-rc2',
                             '1.0.0-rc3',
                             v1.betas.rc2_rc3)
    atct.registerUpgradePath('1.0.0-rc3',
                             '1.0.0-rc4',
                              v1.betas.rc3_rc4)
    atct.registerUpgradePath('1.0.0-rc4',
                             '1.0.0-rc5',
                             null)
    atct.registerUpgradePath('1.0.0-rc5',
                             '1.0.0-final',
                             v1.betas.rc5_final)
    atct.registerUpgradePath('1.0.0-final',
                             '1.0.1-final',
                             null)
    atct.registerUpgradePath('1.0.1-final',
                             '1.0.2-final',
                             v1.final.atct1_0_1_atct1_0_2)
    atct.registerUpgradePath('1.0.2-final',
                             '1.0.3-final',
                             null)
    atct.registerUpgradePath('1.0.3-final',
                             '1.0.4-final',
                             null)
    atct.registerUpgradePath('1.0.4-final',
                             '1.1.0-alpha1',
                             null)
    atct.registerUpgradePath('1.1.0-alpha1',
                             '1.1.0-alpha2',
                             null)
    atct.registerUpgradePath('1.1.0-alpha2',
                             '1.1.0-beta1',
                             null)
    atct.registerUpgradePath('1.1.0-beta1',
                             '1.1.0-beta2',
                             null)
    atct.registerUpgradePath('1.1.0-beta2',
                             '1.1.0-devel (SVN/UNRELEASED)',
                             null)