.PHONY: docs test unittest build clean

PYTHON := $(shell which python)

DOC_DIR        := ./docs
DIST_DIR       := ./dist
WHEELHOUSE_DIR := ./wheelhouse
TEST_DIR       := ./test
SRC_DIR        := ./treevalue

RANGE_DIR      ?= .
RANGE_TEST_DIR := ${TEST_DIR}/${RANGE_DIR}
RANGE_SRC_DIR  := ${SRC_DIR}/${RANGE_DIR}

CYTHON_FILES := $(shell find ${SRC_DIR} -name '*.pyx')

COV_TYPES        ?= xml term-missing
COMPILE_PLATFORM ?= manylinux_2_24_x86_64

build:
	$(PYTHON) setup.py build_ext --inplace \
					$(if ${LINETRACE},--define CYTHON_TRACE,)

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
				2> /dev/null)
	rm -rf ${DIST_DIR} ${WHEELHOUSE_DIR}

test: unittest benchmark

unittest:
	pytest "${RANGE_TEST_DIR}" \
		-sv -m unittest \
		$(shell for type in ${COV_TYPES}; do echo "--cov-report=$$type"; done) \
		--cov="${RANGE_SRC_DIR}" \
		$(if ${MIN_COVERAGE},--cov-fail-under=${MIN_COVERAGE},) \
		$(if ${WORKERS},-n ${WORKERS},)

benchmark:
	pytest "${RANGE_TEST_DIR}" \
		-sv -m benchmark \
		--benchmark-columns=min,max,mean,median,IQR,ops,rounds,iterations \
		--benchmark-disable-gc \
		--benchmark-sort=mean \
		$(if ${WORKERS},-n ${WORKERS},)

docs:
	$(MAKE) -C "${DOC_DIR}" build
pdocs:
	$(MAKE) -C "${DOC_DIR}" prod