from setuptools import setup, find_packages

version = '2.1.17'
long_description = open("README.rst").read()
long_description += "\n"
long_description += open("CHANGES.rst").read()

setup(name='Products.ATContentTypes',
      version=version,
      description="Default Content Types for Plone",
      long_description=long_description,
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          ],
      keywords='Plone Content Types',
      author='AT Content Types development team',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://plone.org/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
          test=[
              'plone.app.blob',
              'zope.annotation',
              'zope.testing',
              'Products.PloneTestCase',
          ]
      ),
      install_requires=[
          'archetypes.referencebrowserwidget',
          'setuptools',
          'plone.i18n',
          'plone.memoize',
          'plone.app.folder',
          'plone.app.layout',
          'zope.component',
          'zope.i18n',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.publisher',
          'zope.tal',
          'Products.CMFPlone',
          'Products.Archetypes',
          'Products.ATReferenceBrowserWidget',  # BBB
          'Products.CMFCore',
          'Products.CMFDynamicViewFTI',
          'Products.CMFDefault',
          'Products.GenericSetup',
          'Products.MimetypesRegistry',
          'Products.PortalTransforms',
          'Products.validation',
          'Acquisition',
          'DateTime',
          'ExtensionClass',
          'transaction',
          'ZConfig',
          'ZODB3',
          'Zope2',
      ],
      )
