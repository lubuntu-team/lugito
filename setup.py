#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import versioneer
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'Flask>=1.0.2',
    'httplib2>=0.12.1',
    'launchpadlib>=1.10.6',
    'phabricator>=0.7.0',
    'versioneer>=0.18',
]

setup_requirements = ['pytest-runner', ]

test_requirements = [
    'pytest',
    'pytest-cov',
]

setup(
    author="Ben Johnston (docEbrown)",
    author_email='bjohnston@neomailbox.net',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Python package to connect services such as irc and launchpad"\
        " to Phabricator and provide updates",
    entry_points={
        'console_scripts': [
            'lugito=lugito.webhooks:run',
        ],
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='lugito',
    name='lugito',
    packages=find_packages(exclude=['*tests']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='',
    zip_safe=False,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
