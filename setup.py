from setuptools import setup, find_packages
from pysimtof.version import __version__

long_description = ''

try:
    from pypandoc import convert

    read_md = lambda f: convert(f, 'rst', 'md')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

classifiers = [
    'Environment :: Console',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Topic :: Scientific/Engineering :: Physics'

]

setup(
    name='pySimToF',
    packages=find_packages(),
    version=__version__,
    description='Collection of tools for dealing with SMS data at storage rings.',
    long_description=read_md('README.md'),
    author='DFreireF // gwgwhc',
    url='https://github.com/DFreireF/pysimtof',
    download_url=f'https://github.com/DFreireF/pysimtof/tarball/{__version__}',
    entry_points={
        'console_scripts': [
            'pysimtof = pysimtof.__main__:main'
        ]
    },
    license='GPLv3',
    keywords=['physics', 'data analysis', 'storage ring', ],
    classifiers=classifiers
)
