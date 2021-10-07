from setuptools import setup, find_packages

import sys


if sys.version_info[0] != 2:
    # Prevent creating or installing a distribution with Python 3.
    raise ValueError("Products.ATContentTypes is based on Archetypes, which is Python 2 only.")

version = '3.0.5'

setup(name='Products.ATContentTypes',
      version=version,
      description="BBB: Default Content Types for Plone 2.1-4.3",
      long_description=(open("README.rst").read() + "\n" +
                        open("CHANGES.rst").read()),
      classifiers=[
          "Development Status :: 6 - Mature",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 2 :: Only",
          "Framework :: Plone",
          "Framework :: Plone :: 5.2",
          "License :: OSI Approved :: GNU General Public License (GPL)",
      ],
      keywords='Plone Content Types',
      author='AT Content Types development team',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://plone.org/',
      license='GPL',
      packages=find_packages(),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      python_requires='==2.7.*',
      extras_require=dict(
          test=[
              'zope.annotation',
              'zope.testing',
              'plone.app.testing',
          ]
      ),
      install_requires=[
          'setuptools',
          'plone.i18n',
          'plone.memoize',
          'plone.app.blob',
          'plone.app.collection',
          'plone.app.folder',
          'plone.app.imaging',
          'plone.app.layout',
          'plone.app.widgets>=1.4.0dev',
          'zope.component',
          'zope.i18n',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.publisher',
          'zope.tal',
          'Products.CMFPlone',
          'Products.Archetypes',
          'Products.CMFCore',
          'Products.CMFDynamicViewFTI',
          'Products.CMFFormController',
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
