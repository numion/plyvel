import glob
import os
from os.path import join, dirname
from setuptools import setup
from setuptools.extension import Extension
import shutil
import sys

CURRENT_DIR = dirname(__file__)

with open(join(CURRENT_DIR, 'plyvel/_version.py')) as fp:
    exec(fp.read(), globals(), locals())


def get_file_contents(filename):
    with open(join(CURRENT_DIR, filename)) as fp:
        return fp.read()


def is_leveldb_source(p):
    suffix = p.split('_')[-1].split('.')[0] 
    return suffix not in ('test', 'bench', 'posix', 'main')


def leveldb_configure(ext, root):
    ext.include_dirs = [root, join(root, 'include')]
    ext.sources.extend(filter(is_leveldb_source,
        glob.glob(join(root, '*/*.cc'))))
    ext.sources.extend(filter(is_leveldb_source,
        glob.glob(join(root, 'helpers/*/*.cc'))))

    if sys.platform == 'win32':
        ext.sources.extend([
            'winleveldb/port/port_win.cc', 'winleveldb/env_win.cc'])
        ext.include_dirs.extend(['winleveldb'])
        ext.libraries = ['Shlwapi', 'Shell32']
        ext.define_macros = [
            ('LEVELDB_PLATFORM_WINDOWS', '1'),
            ('OS_WIN', '1'),
            ('COMPILER_MSVC', '1'),
        ]
        ext.extra_compile_args = ['/EHsc']
        
        shutil.copy('winleveldb/port/port.h', join(root, 'port'))
    else:
        ext.sources.extend([
            join(root, 'port/port_posix.cc'), join(root, 'util/env_posix.cc')])
        ext.libraries = []
        ext.define_macros = [
            ('LEVELDB_PLATFORM_POSIX', '1'),
        ]


def snappy_configure(ext, root):
    ext.include_dirs.append(root)
    ext.sources.extend([
        join(root, 'snappy.cc'),
        join(root, 'snappy-c.cc'),
        join(root, 'snappy-sinksource.cc'),
        join(root, 'snappy-stubs-internal.cc'),
    ])
    ext.define_macros.append(('SNAPPY', '1'))


LEVELDB = Extension(
    'plyvel._plyvel',
    sources=['plyvel/_plyvel.cpp', 'plyvel/comparator.cpp'],
    libraries=['leveldb'],
    extra_compile_args=['-Wall', '-g'],
)

leveldb_root = os.environ.get('PLYVEL_LEVELDB', 'parts/leveldb')
if os.path.exists(leveldb_root):
    leveldb_configure(LEVELDB, leveldb_root)

    snappy_root = os.environ.get('PLYVEL_SNAPPY', 'parts/snappy')
    if os.path.exists(snappy_root):
        snappy_configure(LEVELDB, snappy_root)


setup(
    name='numion-plyvel',
    description="Plyvel, a fast and feature-rich Python interface to LevelDB",
    long_description=get_file_contents('README.rst'),
    url="https://github.com/numion/plyvel",
    version=__version__,
    author="Wouter Bolsterlee",
    author_email="uws@xs4all.nl",
    ext_modules=[LEVELDB],
    packages=['plyvel'],
    license="BSD License",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: C++",
        "Programming Language :: Cython",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
