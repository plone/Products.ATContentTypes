"""AT Content Types migration suite
"""
# Version migration
from Products.ATContentTypes.tool import atct

def executeMigrations():
    from Products.ATContentTypes.migration import v1

def null(portal):
    """ This is a null migration, use it when nothing happens """
    pass

def registerMigrations():
    # so the basic concepts is you put a bunch of migrations in here

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
                             '1.0.5-final',
                             null)
    atct.registerUpgradePath('1.0.5-final',
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
                             '1.1.0-final',
                             null)
    atct.registerUpgradePath('1.1.0-final',
                             '1.1.1-final',
                             null)
    atct.registerUpgradePath('1.1.1-final',
                             '1.2.0-devel (svn/unreleased)',
                             null)
