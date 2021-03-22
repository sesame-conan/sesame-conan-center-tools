#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup


def _get_requires(filename):
    requirements = []
    with open(filename) as req_file:
        for line in req_file.read().splitlines():
            if not line.strip().startswith("#"):
                requirements.append(line)
    return requirements


setup(
    name='sesame-conan-center-tools',
    version='0.1',
    packages=[''],
    url='https://github.com/sesame-conan/sesame-conan-center-tools',
    license='NOT PUBLIC YET',
    author='Orhun Birsoy',
    author_email='orhunbirsoy@gmail.com',
    description='Tools for building and managing Conan Center Index',

    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'sesame=sesame.sesame:run'
        ]
    },
    install_requires=_get_requires('sesame/requirements.txt'),
)
