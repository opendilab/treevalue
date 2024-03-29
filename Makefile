.PHONY: docs test unittest build clean benchmark zip

NO_DEBUG     ?=
NO_DOCSTRING ?=
NO_DEBUG_CMD := $(if ${NO_DOCSTRING},-OO,$(if ${NO_DEBUG},-O,))
PYTHON := $(shell which python) ${NO_DEBUG_CMD}

DOC_DIR        := ./docs
DIST_DIR       := ./dist
WHEELHOUSE_DIR := ./wheelhouse
TEST_DIR       := ./test
BENCHMARK_DIR  := ./benchmark
SRC_DIR        := ./treevalue
RUNS_DIR       := ./runs

RANGE_DIR       ?= .
RANGE_TEST_DIR  := ${TEST_DIR}/${RANGE_DIR}
RANGE_BENCH_DIR := ${BENCHMARK_DIR}/${RANGE_DIR}
RANGE_SRC_DIR   := ${SRC_DIR}/${RANGE_DIR}

CYTHON_FILES := $(shell find ${SRC_DIR} -name '*.pyx')

COV_TYPES        ?= xml term-missing
COMPILE_PLATFORM ?= manylinux_2_24_x86_64

BENCHMARK_FILE       ?=
BENCHMARK_OUTPUT_DIR ?= .benchmarks
BM_FILES             := $(shell find ${BENCHMARK_OUTPUT_DIR} -name '*.json' -type f)
BM_CSV_FILES         := $(addsuffix .csv,$(basename ${BM_FILES}))

build:
	$(PYTHON) setup.py build_ext --inplace \
					$(if ${LINETRACE},--define CYTHON_TRACE,)

zip:
	$(PYTHON) -m build --sdist --outdir ${DIST_DIR}

package:
	$(PYTHON) -m build --sdist --wheel --outdir ${DIST_DIR}
	for whl in `ls ${DIST_DIR}/*.whl`; do \
		auditwheel repair $$whl -w ${WHEELHOUSE_DIR} --plat ${COMPILE_PLATFORM} && \
		cp `ls ${WHEELHOUSE_DIR}/*.whl` ${DIST_DIR} && \
		rm -rf $$whl ${WHEELHOUSE_DIR}/* \
  	; done

clean:
	rm -rf $(shell find ${SRC_DIR} -name '*.so') \
			$(shell ls $(addsuffix .c, $(basename ${CYTHON_FILES})) \
					  $(addsuffix .cpp, $(basename ${CYTHON_FILES})) \
					  $(addsuffix .h, $(basename ${CYTHON_FILES})) \
				2> /dev/null)
	rm -rf ${DIST_DIR} ${WHEELHOUSE_DIR}

test: unittest benchmark

unittest:
	$(PYTHON) -m pytest "${RANGE_TEST_DIR}" \
		-sv -m unittest \
		$(shell for type in ${COV_TYPES}; do echo "--cov-report=$$type"; done) \
		--cov="${RANGE_SRC_DIR}" \
		$(if ${MIN_COVERAGE},--cov-fail-under=${MIN_COVERAGE},) \
		$(if ${WORKERS},-n ${WORKERS},)

benchmark:
	$(PYTHON) -m pytest "${RANGE_TEST_DIR}" \
		-sv -m benchmark \
		--benchmark-columns=min,max,mean,median,IQR,ops,rounds,iterations \
		--benchmark-disable-gc \
		--benchmark-sort=mean \
		$(if ${WORKERS},-n ${WORKERS},) \
		--benchmark-autosave \
		$(if ${BENCHMARK_FILE},--benchmark-save=${BENCHMARK_FILE},)

compare:
	$(PYTHON) -m pytest "${RANGE_BENCH_DIR}" \
		-sv -m benchmark \
		--benchmark-columns=min,max,mean,median,IQR,ops,rounds,iterations \
		--benchmark-disable-gc \
		--benchmark-sort=mean \
		$(if ${WORKERS},-n ${WORKERS},) \
		--benchmark-autosave \
		$(if ${BENCHMARK_FILE},--benchmark-save=${BENCHMARK_FILE},)

%.csv: %.json
	$(PYTHON) bmtrans.py -i "$(shell readlink -f $<)" -o "$(shell readlink -f $@)"
bmtrans: ${BM_CSV_FILES}

docs:
	$(MAKE) -C "${DOC_DIR}" build
pdocs:
	$(MAKE) -C "${DOC_DIR}" prod

run:
	PYTHONPATH=$(shell readlink -f .):$(shell readlink -f ${RUNS_DIR}):${PYTHONPATH} $(MAKE) -C "${RUNS_DIR}" run
