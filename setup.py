from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='profanityfilter',
    version='2.0.4',
    description='A universal Python library for detecting and/or filtering profane words.',
    long_description="",
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='profanity filter clean content',
    packages=find_packages(exclude=['tests']),
    install_requires=['spacy'],
    package_data={
        'profanityfilter': ['data/en_badwords.txt', 'data/ru_badwords.txt'],
    },
    entry_points={
        'console_scripts': [
            'profanityfilter=profanityfilter:main',
        ],
    },
)
