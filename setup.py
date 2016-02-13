#!/usr/bin/env python
import sys
from setuptools import setup, find_packages


dev_requires = [
    'Sphinx==1.2.2',
]

install_requires = [
    'django-gm2m==0.3',
    'nodeconductor>0.85.0',
    # transitive dependency from nodeconductor core requires Pillow version <3.0.0
    'Pillow>=2.0.0,<3.0.0',
]

# RPM installation does not need oslo, cliff and stevedore libs -
# they are required only for installation with setuptools
try:
    action = sys.argv[1]
except IndexError:
    pass
else:
    if action in ['develop', 'install', 'test']:
        install_requires += [
            'cliff==1.7.0',
            'oslo.config==1.4.0',
            'oslo.i18n==1.0.0',
            'oslo.utils==1.0.0',
            'stevedore==1.0.0',
        ]


setup(
    name='nodeconductor-saltstack',
    version='0.1.3',
    author='OpenNode Team',
    author_email='info@opennodecloud.com',
    url='http://nodeconductor.com',
    description='NodeConductor SaltStack plugin allows to manage applications via SaltStack RPC',
    long_description=open('README.rst').read(),
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=install_requires,
    zip_safe=False,
    extras_require={
        'dev': dev_requires,
    },
    entry_points={
        'nodeconductor_extensions': (
            'saltstack = nodeconductor_saltstack.saltstack.extension:SaltStackExtension',
            'exchange = nodeconductor_saltstack.exchange.extension:ExchangeExtension',
            'sharepoint = nodeconductor_saltstack.sharepoint.extension:SharepointExtension',
        ),
    },
    # tests_require=tests_requires,
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
    ],
)