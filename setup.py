#!/usr/bin/env python
from setuptools import setup

try:
    with open('README.rst') as file:
        long_description = file.read()
except IOError:
    long_description = "missing"


setup(
    name='segtok',
    version='1.5.2',
    url='https://github.com/fnl/segtok',
    author='Florian Leitner',
    author_email='florian.leitner@gmail.com',
    description='sentence segmentation and word tokenization tools',
    keywords='sentence segmenter splitter split word tokenizer token',
    license='MIT',
    packages=['segtok'],
    install_requires=['regex'],  # handles all Unicode categories in Regular Expressions
    long_description=long_description,
    entry_points={
        'console_scripts': [
            'tokenizer = segtok.tokenizer:main',
            'segmenter = segtok.segmenter:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Linguistic',
    ],
)
