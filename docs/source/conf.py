# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

import os
import sys
from datetime import datetime
from subprocess import Popen

import where
from packaging import version as version_

from treevalue.config.meta import __TITLE__, __AUTHOR__, __VERSION__

if not os.environ.get("NO_IMAGES_BUILD"):
    print("Building diagrams and graphviz...")
    diagrams = Popen([where.first('make'), '-f', "diagrams.mk", "build"], stdout=sys.stdout, stderr=sys.stderr)
    if diagrams.wait() != 0:
        raise ChildProcessError("Diagrams failed with %d." % (diagrams.returncode,))

    graphviz = Popen([where.first('make'), '-f', "graphviz.mk", "build"], stdout=sys.stdout, stderr=sys.stderr)
    if graphviz.wait() != 0:
        raise ChildProcessError("Graphviz failed with %d." % (graphviz.returncode,))

    demos = Popen([where.first('make'), '-f', "demos.mk", "build"], stdout=sys.stdout, stderr=sys.stderr)
    if demos.wait() != 0:
        raise ChildProcessError("Demos failed with %d." % (demos.returncode,))

    print("Build of diagrams and graphviz complete.")

project = __TITLE__
copyright = '{year}, {author}'.format(year=datetime.now().year, author=__AUTHOR__)
author = __AUTHOR__

# The short X.Y version
version = version_.parse(__VERSION__).base_version
# The full version, including alpha/beta/rc tags
release = __VERSION__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.todo',
    'sphinx.ext.graphviz',
    'enum_tools.autoenum',
    "sphinx_multiversion",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
htmlhelp_basename = 'TreeValue'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

epub_title = project
epub_exclude_files = ['search.html']

# Whitelist pattern for tags (set to None to ignore all tags)
smv_tag_whitelist = r'^v.*$'  # Include all tags start with 'v'
smv_branch_whitelist = r'^.*$'  # Include all branches
smv_remote_whitelist = r'^.*$'  # Use branches from all remotes
smv_released_pattern = r'^tags/.*$'  # Tags only
smv_outputdir_format = '{ref.name}'  # Use the branch/tag name

graphviz_output_format = 'svg'
