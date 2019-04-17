#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import versioneer

setup(
    name='vial',
    author="doubleO8",
    author_email="wb008@hdm-stuttgart.de",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='flask utilities library',
    long_description="flask utilities library",
    url="https://github.com/doubleO8/vial",
    packages=['vial'],
    install_requires=['pytz', 'flask'],
)
