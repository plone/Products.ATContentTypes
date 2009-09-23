import os
from setuptools import setup, find_packages

version = '1.3.5'

setup(name='Products.ATContentTypes',
      version=version,
      description="Default Content Types for Plone",
      long_description=open("README.txt").read() + "\n" + \
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
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
      install_requires=[
          'setuptools',
          'Products.CMFCore',
          'Products.Archetypes',
          'Plone',
          'Products.CMFDynamicViewFTI',
          'zope.interface',
          'zope.tal',
          'zope.app.container',
          'zope.component',
          'simplejson',
          'plone.memoize',
      ],
      )
