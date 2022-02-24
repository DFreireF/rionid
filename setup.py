from setuptools import setup, find_packages
from pysimtof.version import __version__
from pathlib import Path

this_directory=Path(__file__).parent
long_description=(this_directory / 'README.md').read_text()

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
    long_description=long_description,
    long_description_content_type='text/markdown',
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
