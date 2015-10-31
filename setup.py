#!/usr/bin/env python

from setuptools import setup

# TODO: Handle automatic versioning from build system
VERSION = '0.0.0'

setup(
    name='yarn',
    version=VERSION,
    description='Yarn is a tool for remote command execution and product deployment.',
    author='Jason L McFarland',
    author_email='jason.mcfarland1976+python-yarn@gmail.com',
    packages=['yarn',],
    test_suite='nose.collector',
    tests_require=['nose', 'paramiko'],
    install_requires=['paramiko>=1.13'],
    entry_points = {'console_scripts': ['yarn = yarn.yarn:main',]},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Python Modules',
        'Topic :: System',
        'Topic :: Software Distribution',
        'Topic :: System :: Clustering',
        'Topic :: System :: Systems Administration',
    ],
)
