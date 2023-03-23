from setuptools import setup, find_packages
from pysimtof.version import __version__
from pathlib import Path

this_directory=Path(__file__).parent
long_description=(this_directory / 'README.md').read_text()

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Topic :: Scientific/Engineering :: Physics'
]

setup(
    name='pysimtof',
    version=__version__,
    description='Collection of tools for dealing with SMS data at storage rings.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='DFreireF // gwgwhc',
    url='https://github.com/DFreireF/pysimtof',
    download_url=f'https://github.com/DFreireF/pysimtof/archive/{__version__}.tar.gz',
    packages=find_packages(),
    classifiers=classifiers,
    keywords=['physics', 'data analysis', 'storage ring'],
    python_requires='>=3.7, <4',
    install_requires=[
        'iqtools',
        'barion',
        'lisereader',
    ],
    entry_points={
        'console_scripts': [
            'pysimtof = pysimtof.__main__:main'
        ]
    },
    license='GPLv3',
)
