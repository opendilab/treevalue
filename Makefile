.PHONY: docs test unittest

WORKERS  ?=

RANGE_DIR      ?= .
BASE_TEST_DIR  := ./test
BASE_PROJ_DIR  := ./treevalue
RANGE_TEST_DIR := ${BASE_TEST_DIR}/${RANGE_DIR}
RANGE_PROJ_DIR := ${BASE_PROJ_DIR}/${RANGE_DIR}

DOC_DIR := ./docs

test: unittest

unittest:
		pytest "${RANGE_TEST_DIR}" \
			-sv -m unittest \
			--cov-report term-missing --cov="${RANGE_PROJ_DIR}" \
			$(if ${MIN_COVERAGE},--cov-fail-under=${MIN_COVERAGE},) \
			$(if ${WORKERS},-n ${WORKERS},)

docs:
	$(MAKE) -C "${DOC_DIR}" html
