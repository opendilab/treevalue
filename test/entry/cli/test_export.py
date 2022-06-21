import bz2
import gzip
import os
import zlib

import pytest
from click.testing import CliRunner

from treevalue import FastTreeValue, load
from treevalue.entry.cli import treevalue_cli

t1 = FastTreeValue({'a': 1, 'b': [2] * 1000, 'x': {'c': 3, 'd': 4}})
t2 = FastTreeValue({'a': 1, 'b': {2, 4}, 'x': {'c': [1, 3] * 500, 'd': 4}})
t3 = FastTreeValue({'a': 1, 'b': 2, 'x': {'c': t1.b, 'd': t2.x.c}})


def _my_compress(d):
    return bz2.compress(gzip.compress(zlib.compress(d)))


def _my_decompress(d):
    return zlib.decompress(gzip.decompress(bz2.decompress(d)))


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestEntryCliExport:
    def test_simple_export(self):
        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            result = runner.invoke(treevalue_cli, ['export', '-t', 'test.entry.cli.test_export.t1'])

            assert result.exit_code == 0, f'Runtime Error (exitcode {result.exit_code}), ' \
                                          f'The output is:\n{result.output}'
            assert os.path.exists('t1.btv')
            assert os.path.getsize('t1.btv') < 240

            with open('t1.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t1

    def test_multiple_export(self):
        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            result = runner.invoke(treevalue_cli, ['export', '-t', 'test.entry.cli.test_export.*'])

            assert result.exit_code == 0, f'Runtime Error (exitcode {result.exit_code}), ' \
                                          f'The output is:\n{result.output}'
            assert os.path.exists('t1.btv')
            assert os.path.getsize('t1.btv') < 240
            assert os.path.exists('t2.btv')
            assert os.path.getsize('t2.btv') < 290
            assert os.path.exists('t3.btv')
            assert os.path.getsize('t3.btv') < 260

            with open('t1.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t1
            with open('t2.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t2
            with open('t3.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t3

        with runner.isolated_filesystem():
            result = runner.invoke(treevalue_cli, ['export', '-t', 'test.entry.cli.test_export.t[23]'])

            assert result.exit_code == 0, f'Runtime Error (exitcode {result.exit_code}), ' \
                                          f'The output is:\n{result.output}'
            assert not os.path.exists('t1.btv')
            assert os.path.exists('t2.btv')
            assert os.path.getsize('t2.btv') < 290
            assert os.path.exists('t3.btv')
            assert os.path.getsize('t3.btv') < 260

            with open('t2.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t2
            with open('t3.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t3

    def test_multiple_export_without_compression(self):
        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            with pytest.warns(None):
                result = runner.invoke(treevalue_cli, ['export', '-t', 'test.entry.cli.test_export.*', '-r'])

            assert result.exit_code == 0, f'Runtime Error (exitcode {result.exit_code}), ' \
                                          f'The output is:\n{result.output}'
            assert os.path.exists('t1.btv')
            assert os.path.getsize('t1.btv') < 2170
            assert os.path.exists('t2.btv')
            assert os.path.getsize('t2.btv') < 2220
            assert os.path.exists('t3.btv')
            assert os.path.getsize('t3.btv') < 4170

            with open('t1.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t1
            with open('t2.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t2
            with open('t3.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t3

        with runner.isolated_filesystem():
            with pytest.warns(RuntimeWarning):
                result = runner.invoke(treevalue_cli, ['export', '-t', 'test.entry.cli.test_export.*',
                                                       '-r', '-c', 'zlib'])

            assert result.exit_code == 0, f'Runtime Error (exitcode {result.exit_code}), ' \
                                          f'The output is:\n{result.output}'
            assert os.path.exists('t1.btv')
            assert os.path.getsize('t1.btv') < 2170
            assert os.path.exists('t2.btv')
            assert os.path.getsize('t2.btv') < 2230
            assert os.path.exists('t3.btv')
            assert os.path.getsize('t3.btv') < 4170

            with open('t1.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t1
            with open('t2.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t2
            with open('t3.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t3

    def test_multiple_export_with_compress_define(self):
        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            result = runner.invoke(treevalue_cli, ['export', '-t', 'test.entry.cli.test_export.*',
                                                   '-c', 'gzip'])

            assert result.exit_code == 0, f'Runtime Error (exitcode {result.exit_code}), ' \
                                          f'The output is:\n{result.output}'
            assert os.path.exists('t1.btv')
            assert os.path.getsize('t1.btv') < 220
            assert os.path.exists('t2.btv')
            assert os.path.getsize('t2.btv') < 240
            assert os.path.exists('t3.btv')
            assert os.path.getsize('t3.btv') < 210

            with open('t1.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t1
            with open('t2.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t2
            with open('t3.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t3

        with runner.isolated_filesystem():
            result = runner.invoke(treevalue_cli, [
                'export', '-t', 'test.entry.cli.test_export.*',
                '-c', 'test.entry.cli.test_export._my_compress:test.entry.cli.test_export._my_decompress'
            ])

            assert result.exit_code == 0, f'Runtime Error (exitcode {result.exit_code}), ' \
                                          f'The output is:\n{result.output}'
            assert os.path.exists('t1.btv')
            assert os.path.getsize('t1.btv') < 330
            assert os.path.exists('t2.btv')
            assert os.path.getsize('t2.btv') < 430
            assert os.path.exists('t3.btv')
            assert os.path.getsize('t3.btv') < 375

            with open('t1.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t1
            with open('t2.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t2
            with open('t3.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t3

    def test_with_od(self):
        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            os.mkdir('subpath')
            with pytest.warns(RuntimeWarning):
                result = runner.invoke(treevalue_cli, [
                    'export', '-t', 'test.entry.cli.test_export.t[23]',
                    '-o', 'subpath/t1.btv',
                    '-o', 'subpath/t2.btv',
                    '-o', 'subpath/t3.btv',
                ])

            assert result.exit_code == 0, f'Runtime Error (exitcode {result.exit_code}), ' \
                                          f'The output is:\n{result.output}'
            assert os.path.exists('subpath/t1.btv')
            assert os.path.getsize('subpath/t1.btv') < 290
            assert os.path.exists('subpath/t2.btv')
            assert os.path.getsize('subpath/t2.btv') < 260
            assert not os.path.exists('subpath/t3.btv')

            with open('subpath/t1.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t2
            with open('subpath/t2.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t3

        with runner.isolated_filesystem():
            os.mkdir('subpath')
            with pytest.warns(RuntimeWarning):
                result = runner.invoke(treevalue_cli, [
                    'export', '-t', 'test.entry.cli.test_export.t[23]',
                    '-o', 't1.btv',
                    '-o', 't2.btv',
                    '-o', 't3.btv',
                    '-d', 'subpath',
                ])

            assert result.exit_code == 0, f'Runtime Error (exitcode {result.exit_code}), ' \
                                          f'The output is:\n{result.output}'
            assert os.path.exists('subpath/t1.btv')
            assert os.path.getsize('subpath/t1.btv') < 290
            assert os.path.exists('subpath/t2.btv')
            assert os.path.getsize('subpath/t2.btv') < 260
            assert not os.path.exists('subpath/t3.btv')

            with open('subpath/t1.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t2
            with open('subpath/t2.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t3

        with runner.isolated_filesystem():
            os.mkdir('subpath')
            with pytest.warns(None):
                result = runner.invoke(treevalue_cli, [
                    'export', '-t', 'test.entry.cli.test_export.t[23]',
                    '-d', 'subpath',
                ])

            assert result.exit_code == 0, f'Runtime Error (exitcode {result.exit_code}), ' \
                                          f'The output is:\n{result.output}'
            assert not os.path.exists('subpath/t1.btv')
            assert os.path.exists('subpath/t2.btv')
            assert os.path.getsize('subpath/t2.btv') < 290
            assert os.path.exists('subpath/t3.btv')
            assert os.path.getsize('subpath/t3.btv') < 260

            with open('subpath/t2.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t2
            with open('subpath/t3.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t3

        with runner.isolated_filesystem():
            with pytest.warns(None):
                result = runner.invoke(treevalue_cli, [
                    'export', '-t', 'test.entry.cli.test_export.t[23]',
                    '-o', 'ppp.btv'
                ])

            assert result.exit_code == 0, f'Runtime Error (exitcode {result.exit_code}), ' \
                                          f'The output is:\n{result.output}'
            assert not os.path.exists('t1.btv')
            assert not os.path.exists('t2.btv')
            assert os.path.exists('ppp.btv')
            assert os.path.getsize('ppp.btv') < 290
            assert os.path.exists('t3.btv')
            assert os.path.getsize('t3.btv') < 260

            with open('ppp.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t2
            with open('t3.btv', 'rb') as file:
                assert load(file, type_=FastTreeValue) == t3
