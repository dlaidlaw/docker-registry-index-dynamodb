#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import setuptools
except ImportError:
    import distutils.core as setuptools


__title__ = 'docker-registry-index-dynamodb'
__author__ = 'Don Laidlaw'
__copyright__ = 'Copyright 2014'
__credits__ = []

__version__ = '0.1.0'

__email__ = 'don@donlaidlaw.ca'
__url__ = 'https://github.com/donlaidlaw/docker-registry-index-dynamodb'
__description__ = 'Docker registry Amazon AWS DynamoDB index database'
#d = 'https://github.com/dlaidlaw/docker-registry-index-dynamodb/archive/master.zip'

setuptools.setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email=__email__,
    maintainer=__author__,
    maintainer_email=__email__,
    url=__url__,
    description=__description__,
    long_description=open('./README.md').read(),
    platforms=['Independent'],
    license=open('./LICENSE').read(),
    packages=['docker_registry_index'],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 # 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 # 'Programming Language :: Python :: 3.2',
                 # 'Programming Language :: Python :: 3.3',
                 # 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: Implementation :: CPython',
                 'Operating System :: OS Independent',
                 'Topic :: Utilities',
                 'License :: OSI Approved :: Apache Software License'],
    install_requires=open('./requirements.txt').read(),
    keywords='docker registry index dynamodb',

)