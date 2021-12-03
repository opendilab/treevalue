import os
import re
from codecs import open
from distutils.core import setup

from setuptools import find_packages
from Cython.Build import cythonize  # this line should be after 'from setuptools import find_packages'

_package_name = "treevalue"

here = os.path.abspath(os.path.dirname(__file__))
meta = {}
with open(os.path.join(here, _package_name, 'config', 'meta.py'), 'r', 'utf-8') as f:
    exec(f.read(), meta)


def _load_req(file: str):
    with open(file, 'r', 'utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip()]


requirements = _load_req('requirements.txt')

_REQ_PATTERN = re.compile('^requirements-([a-zA-Z0-9_]+)\\.txt$')
group_requirements = {
    item.group(1): _load_req(item.group(0))
    for item in [_REQ_PATTERN.fullmatch(reqpath) for reqpath in os.listdir()] if item
}

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()


def find_pyx(path='.'):
    pyx_files = []
    for root, dirs, filenames in os.walk(path):
        for fname in filenames:
            if fname.endswith('.pyx'):
                pyx_files.append(os.path.join(root, fname))
    return pyx_files


_LINETRACE = not not os.environ.get('LINETRACE', None)

setup(
    # information
    name=meta['__TITLE__'],
    version=meta['__VERSION__'],
    packages=find_packages(
        include=(_package_name, "%s.*" % _package_name)
    ),
    description=meta['__DESCRIPTION__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    author=meta['__AUTHOR__'],
    author_email=meta['__AUTHOR_EMAIL__'],
    license='Apache License, Version 2.0',
    keywords='Tree-structured Value Management',
    url='https://github.com/HansBug/treevalue',

    # environment
    python_requires=">=3.6",
    ext_modules=cythonize(
        find_pyx(),
        language_level=3,
        compiler_directives=dict(
            linetrace=_LINETRACE,
        )
    ),
    install_requires=requirements,
    tests_require=group_requirements['test'],
    extras_require=group_requirements,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'console_scripts': [
            'treevalue=treevalue.entry.cli:treevalue_cli'
        ]
    },
)
