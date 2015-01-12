from setuptools import setup

try:
    with open('README.rst') as file:
        long_description = file.read()
except IOError:
    long_description = "missing"


setup(
    name='segtok',
    version='1.1.1',
    url='https://github.com/fnl/segtok',
    author='Florian Leitner',
    author_email='florian.leitner@gmail.com',
    description='sentence segmentation and word tokenization tools',
    keywords='sentence segmenter splitter word tokenizer token',
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
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Linguistic',
    ],
)
