# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Jonathan M. Lange <jml@mumak.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This is a copy of https://github.com/jml/tree-format, with a few modifications,
# its based commit id is 4c6de1074d96129b7e03eecdf42fac2cde3b5151.
# And in this library 'treevalue', Apache Licence Version 2.0 is used as well.

r"""
Overview:
    Library for formatting trees.

    This is a copy of https://github.com/jml/tree-format, with a few modifications,
    its based commit id is 4c6de1074d96129b7e03eecdf42fac2cde3b5151.

Changes:
    - The ``NEWLINE`` value is modified to empty string for the vision of final tree.
    - The ``print_tree`` function is removed because it is nowhere to be used in our case.
    - Add ``__doc__`` for ``format_tree`` function.
    - All the ``\n`` strings are replaced to ``os.linesep``.
    - The code is reformatted.
"""

import itertools
import os

FORK = u'\u251c'
LAST = u'\u2514'
VERTICAL = u'\u2502'
HORIZONTAL = u'\u2500'
NEWLINE = u''


def _format_newlines(prefix, formatted_node):
    """
    Convert newlines into U+23EC characters, followed by an actual newline and
    then a tree prefix so as to position the remaining text under the previous
    line.
    """
    replacement = u''.join([NEWLINE, os.linesep, prefix])
    return replacement.join(formatted_node.splitlines())


def _format_tree(node, format_node, get_children, prefix=u''):
    children = list(get_children(node))
    next_prefix = u''.join([prefix, VERTICAL, u'   '])
    for child in children[:-1]:
        yield u''.join([
            prefix, FORK, HORIZONTAL, HORIZONTAL, u' ',
            _format_newlines(next_prefix, format_node(child))])
        for result in _format_tree(child, format_node, get_children, next_prefix):
            yield result
    if children:
        last_prefix = u''.join([prefix, u'    '])
        yield u''.join([
            prefix, LAST, HORIZONTAL, HORIZONTAL, u' ',
            _format_newlines(last_prefix, format_node(children[-1]))])
        for result in _format_tree(children[-1], format_node, get_children, last_prefix):
            yield result


def format_tree(node, format_node, get_children) -> str:
    r"""
    Overview:
        Format the given tree.

    Arguments:
        - node: Node object
        - format_node: Format node getter
        - get_children: Children getter.

    Returns:
        - formatted: Formatted string.

    Example:
        >>> from operator import itemgetter
        >>>
        >>> from tree_format import format_tree
        >>>
        >>> tree = (
        >>>     'foo', [
        >>>         ('bar', [
        >>>             ('a', []),
        >>>             ('b', []),
        >>>         ]),
        >>>         ('baz', []),
        >>>         ('qux', [
        >>>             ('c\nd', []),
        >>>         ]),
        >>>     ],
        >>> )
        >>> format_tree(tree, format_node=itemgetter(0), get_children=itemgetter(1))
        foo
        ├── bar
        │   ├── a
        │   └── b
        ├── baz
        └── qux
            └── c
                d
    """
    lines = itertools.chain(
        [format_node(node)],
        _format_tree(node, format_node, get_children),
        [u''],
    )
    return os.linesep.join(lines)
