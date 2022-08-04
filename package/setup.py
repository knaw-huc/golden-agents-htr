#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md', encoding='utf8') as f:
    readme = f.read()

setup(
    name='golden_agents_ner',
    version='0.1.1',

    description='NER pipeline and utility functions for the Golden Agents project',
    long_description=readme,
    long_description_content_type='text/markdown',

    author='Bram Buitendijk <bram.buitendijk@di.huc.knaw.nl>, Maarten van Gompel <proycon@anaproy.nl>',
    author_email='bram.buitendijk@di.huc.knaw.nl',

    url='https://github.com/knaw-huc/golden-agents-htr/package',
    license='GPLv3',

    packages=find_packages(exclude=('tests', 'docs')),

    entry_points={
        'console_scripts': [
            'golden-agents-ner = golden_agents_ner.cli:main'
        ]
    }
)
