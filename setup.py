#!/usr/bin/env python3
"""Lupulib setup script."""
from setuptools import setup, find_packages
from lupulib.constants import (VERSION, PROJECT_PACKAGE_NAME,
                              PROJECT_LICENSE, PROJECT_URL,
                              PROJECT_DESCRIPTION, PROJECT_AUTHOR,
                              PROJECT_LONG_DESCRIPTION)

PACKAGES = find_packages()

setup(
    name=PROJECT_PACKAGE_NAME,
    version=VERSION,
    description=PROJECT_DESCRIPTION,
    long_description=PROJECT_LONG_DESCRIPTION,
    author=PROJECT_AUTHOR,
    license=PROJECT_LICENSE,
    url=PROJECT_URL,
    platforms='any',
    py_modules=['lupulib'],
    packages=PACKAGES,
    keywords='smart home automation',
    include_package_data=True,
    python_requires='>=3.5',
    install_requires=[
        'requests>=2.12.4',
        'pyyaml',
        'colorlog'
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'lupulib = lupulib.__main__:main'
        ]
    }
)