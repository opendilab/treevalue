import os
import pathlib
import pickle
import warnings
import zlib

import pytest
from click.testing import CliRunner

from treevalue import FastTreeValue, dump, graphics
from treevalue.entry.cli import treevalue_cli

t1 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': 3, 'd': 4}})
t2 = FastTreeValue({'a': 1, 'b': {2, 4}, 'x': {'c': [1, 3], 'd': 4}})
t3 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': t2.b, 'd': t2.x.c}})

g = graphics(
    (t1, 't1'), (t2, 't2'), (t3, 't3'),
    title='This is title for g.',
    cfg=dict(bgcolor='#ffffff00'),
    dup_value=(list,),
)


@pytest.mark.unittest
class TestEntryCliGraph:
    def test_simple_code_graph(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                treevalue_cli,
                args=['graph', '-t', 'test.entry.cli.test_graph.t1',
                      '-o', 'test_graph.svg', '-o', 'test_graph.gv'],
            )

            assert result.exit_code == 0
            assert os.path.exists('test_graph.svg')
            assert os.path.getsize('test_graph.svg') <= 7000
            assert os.path.exists('test_graph.gv')
            assert os.path.getsize('test_graph.gv') <= 2500

    def test_simple_code_graph_to_stdout(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with pytest.warns(RuntimeWarning):
                result = runner.invoke(
                    treevalue_cli,
                    args=['graph', '-t', 'test.entry.cli.test_graph.t1',
                          '-o', 'test_graph.svg', '-o', 'test_graph.gv', '-O'],
                )

            assert result.exit_code == 0
            assert not os.path.exists('test_graph.svg')
            assert not os.path.exists('test_graph.gv')
            assert len(result.output) <= 2500

    def test_simple_code_multiple_graph(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                treevalue_cli,
                args=['graph', '-t', 'test.entry.cli.test_graph.t[12]', '-o', 'test_graph.svg'],
            )

            assert result.exit_code == 0
            assert os.path.exists('test_graph.svg')
            assert os.path.getsize('test_graph.svg') <= 13000

        with runner.isolated_filesystem():
            result = runner.invoke(
                treevalue_cli,
                args=['graph', '-t', 'test.entry.cli.test_graph.*', '-o', 'test_graph.svg'],
            )

            assert result.exit_code == 0
            assert os.path.exists('test_graph.svg')
            assert os.path.getsize('test_graph.svg') <= 17500

    def test_simple_binary_graph(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('g1.bg', 'wb') as file:
                dump(t1, file, compress=zlib)

            result = runner.invoke(
                treevalue_cli,
                args=['graph', '-t', 'g1.bg', '-o', 'test_graph.svg'],
            )

            assert result.exit_code == 0
            assert os.path.exists('test_graph.svg')
            assert os.path.getsize('test_graph.svg') <= 6500

        with runner.isolated_filesystem():
            with open('g1.bg', 'wb') as file:
                dump(t1, file, compress=zlib)
            with open('g2.bg', 'wb') as file:
                dump(t2, file, compress=zlib)
            with open('g3.bg', 'wb') as file:
                dump(t3, file, compress=zlib)

            result = runner.invoke(
                treevalue_cli,
                args=['graph', '-t', '*.bg', '-o', 'test_graph.svg'],
            )

            assert result.exit_code == 0
            assert os.path.exists('test_graph.svg')
            assert os.path.getsize('test_graph.svg') <= 17500

        with runner.isolated_filesystem():
            with open('test.entry.cli.test_graph.t1', 'wb') as file:
                dump(t2, file, compress=zlib)

            result = runner.invoke(
                treevalue_cli,
                args=['graph', '-t', 'test.entry.cli.test_graph.t1', '-o', 'test_graph.svg'],
            )

            assert result.exit_code == 0
            assert os.path.exists('test_graph.svg')
            assert os.path.getsize('test_graph.svg') <= 13000

        with runner.isolated_filesystem():
            with open('test.entry.cli.test_graph.t1', 'wb') as file:
                pickle.dump([1, 2, 3], file)

            result = runner.invoke(
                treevalue_cli,
                args=['graph', '-t', 'test.entry.cli.test_graph.t1', '-o', 'test_graph.svg'],
            )

            assert result.exit_code == 0
            assert os.path.exists('test_graph.svg')
            assert os.path.getsize('test_graph.svg') <= 6500

    def test_duplicates(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                treevalue_cli,
                args=['graph', '-t', 'test.entry.cli.test_graph.t[23]', '-D',
                      '-o', 'test_graph.svg'],
            )

            assert result.exit_code == 0
            assert os.path.exists('test_graph.svg')
            assert os.path.getsize('test_graph.svg') <= 12000

        _p = os.path.abspath(os.curdir)
        with runner.isolated_filesystem():
            result = runner.invoke(
                treevalue_cli,
                args=['graph', '-t', 'test.entry.cli.test_graph.t[23]',
                      '-d', 'list', '-d', 'set',
                      '-o', 'test_graph.svg'],
            )

            assert result.exit_code == 0
            assert os.path.exists('test_graph.svg')
            import shutil
            shutil.copy('test_graph.svg', os.path.join(_p, 'test_graph.svg'))
            assert os.path.getsize('test_graph.svg') <= 11000

    def test_graph(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with pytest.warns(RuntimeWarning):
                result = runner.invoke(
                    treevalue_cli,
                    args=['graph', '-g', 'test.entry.cli.test_graph.g',
                          '-t', 'first title', '-o', 'test_graph.svg'],
                )

            assert result.exit_code == 0
            assert os.path.exists('test_graph.svg')
            assert os.path.getsize('test_graph.svg') <= 16500

            content = pathlib.Path('test_graph.svg').read_text()
            assert 'first title' not in content
            assert 'This is title for g.' in content

    def test_cfg(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                treevalue_cli,
                args=['graph', '-t', 'test.entry.cli.test_graph.*',
                      '-c', 'bgcolor=#ffffff00', '-O'],
            )

            assert result.exit_code == 0
            assert len(result.output) <= 6000
            assert '#ffffff00' in result.output

        with runner.isolated_filesystem():
            result = runner.invoke(
                treevalue_cli,
                args=['graph', '-t', 'test.entry.cli.test_graph.*',
                      '-c', 'bgcolor#ffffff00', '-O'],
            )

            assert result.exit_code != 0
            assert "Configuration should be KEY=VALUE, but 'bgcolor#ffffff00' found." in result.output

    def test_file_with_invalid_permission(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('g1.bg', 'wb') as file:
                dump(t1, file, compress=zlib)

            try:
                os.chmod('g1.bg', int('000', base=8))
            except PermissionError:
                warnings.warn(RuntimeWarning('Permission denied when changing the permission, skip this test.'))
            else:
                result = runner.invoke(
                    treevalue_cli,
                    args=['graph', '-t', 'g1.bg', '-o', 'test_graph.svg'],
                )

                assert result.exit_code == 0
                assert os.path.exists('test_graph.svg')
                assert os.path.getsize('test_graph.svg') <= 1000
