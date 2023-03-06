.PHONY: clean

JUPYTER ?= $(shell which jupyter)
NBCONVERT ?= ${JUPYTER} nbconvert

SOURCE  ?= .
IPYNBS  := $(shell find ${SOURCE} -name *.ipynb | grep -v .ipynb_checkpoints)

clean:
	for nb in ${IPYNBS}; do \
		if [ -f $$nb ]; then \
			$(NBCONVERT) --clear-output --inplace $$nb; \
		fi; \
	done;