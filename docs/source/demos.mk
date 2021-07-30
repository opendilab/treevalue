PYTHON := $(shell which python)

SOURCE         ?= .
PYTHON_DEMOS   := $(shell find ${SOURCE} -name *.demo.py)
PYTHON_RESULTS := $(addsuffix .py.txt, $(basename ${PYTHON_DEMOS}))
SHELL_DEMOS    := $(shell find ${SOURCE} -name *.demo.sh)
SHELL_RESULTS  := $(addsuffix .sh.txt, $(basename ${SHELL_DEMOS}))

%.demo.py.txt: %.demo.py
	cd "$(shell dirname $(shell readlink -f $<))" && \
		PYTHONPATH="$(shell dirname $(shell readlink -f $<)):${PYTHONPATH}" \
		$(PYTHON) "$(shell readlink -f $<)" > "$(shell readlink -f $@)"

%.demo.sh.txt: %.demo.sh
	cd "$(shell dirname $(shell readlink -f $<))" && \
		$(SHELL) "$(shell readlink -f $<)" > "$(shell readlink -f $@)"

build: ${PYTHON_RESULTS} ${SHELL_RESULTS}

all: build

clean:
	rm -rf \
		$(shell find ${SOURCE} -name *.py.txt) \
		$(shell find ${SOURCE} -name *.sh.txt) \
		$(shell find ${SOURCE} -name *.dat.*)
