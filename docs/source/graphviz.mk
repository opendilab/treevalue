DOT := $(shell which dot)

SOURCE ?= .
DOTS   := $(shell find ${SOURCE} -name *.dot)
PNGS   := $(addsuffix .dot.png, $(basename ${DOTS}))
SVGS   := $(addsuffix .dot.svg, $(basename ${DOTS}))

%.dot.png: %.dot
	$(DOT) -Tpng -o$@ $<

%.dot.svg: %.dot
	$(DOT) -Tsvg -o$@ $<

build: ${SVGS} ${PNGS}

all: build

clean:
	rm -rf \
		$(shell find ${SOURCE} -name *.dot.svg) \
		$(shell find ${SOURCE} -name *.dot.png) \
