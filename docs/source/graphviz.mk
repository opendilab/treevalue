DOT := $(shell which dot)

SOURCE ?= .
GVS    := $(shell find ${SOURCE} -name *.gv)
PNGS   := $(addsuffix .gv.png, $(basename ${GVS}))
SVGS   := $(addsuffix .gv.svg, $(basename ${GVS}))

%.gv.png: %.gv
	$(DOT) -Tpng -o$@ $<

%.gv.svg: %.gv
	$(DOT) -Tsvg -o$@ $<

build: ${SVGS} ${PNGS}

all: build

clean:
	rm -rf \
		$(shell find ${SOURCE} -name *.gv.svg) \
		$(shell find ${SOURCE} -name *.gv.png) \
