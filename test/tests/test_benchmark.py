import pytest


@pytest.mark.benchmark(group="system")
class TestSystemBenchmark:
    def test_empty_func(self, benchmark):
        def empty_func():
            pass

        benchmark(empty_func)
