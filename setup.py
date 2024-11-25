# -*- coding: utf-8 -*-
from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='profanityfilter',
    version='2.0.6',
    description='A universal Python library for detecting and/or filtering profane words.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/areebbeigh/profanityfilter',
    author='Areeb Beigh',
    author_email='areebbeigh@gmail.com',
    license='BSD',
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='profanity filter clean content',
    packages=find_packages(exclude=['tests']),
    install_requires=['inflection'],
    package_data={
        'profanityfilter': ['data/badwords.txt'],
    },
    entry_points={
        'console_scripts': [
            'profanityfilter=profanityfilter:main',
        ],
    },
)
