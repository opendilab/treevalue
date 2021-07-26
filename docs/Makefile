# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS         ?=
SPHINXBUILD        ?= $(shell which sphinx-build)
SPHINXMULTIVERSION ?= $(shell which sphinx-multiversion)
SOURCEDIR          ?= source
BUILDDIR           ?= build

# Minimal makefile for Sphinx documentation
DIAGRAMS_MK := ${SOURCEDIR}/diagrams.mk
DIAGRAMS    := $(MAKE) -f "${DIAGRAMS_MK}" SOURCE=${SOURCEDIR}
GRAPHVIZ_MK := ${SOURCEDIR}/graphviz.mk
GRAPHVIZ    := $(MAKE) -f "${GRAPHVIZ_MK}" SOURCE=${SOURCEDIR}

.EXPORT_ALL_VARIABLES:

PYTHONPATH = $(shell if [ `which git` ]; then git rev-parse --show-toplevel; else readlink -f ..; fi)
NO_IMAGES_BUILD = true

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help diagrams build html prod clean sourcedir builddir Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
diagrams:
	@$(DIAGRAMS) build
	@$(GRAPHVIZ) build
build: html
html: diagrams
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@touch "$(BUILDDIR)/html/.nojekyll"
prod: diagrams
	@$(SPHINXMULTIVERSION) "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@cp main_page.html "$(BUILDDIR)/html/index.html"
	@touch "$(BUILDDIR)/html/.nojekyll"

clean:
	@$(DIAGRAMS) clean
	@$(GRAPHVIZ) clean
	@$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

sourcedir:
	@echo $(shell readlink -f ${SOURCEDIR})
builddir:
	@echo $(shell readlink -f ${BUILDDIR}/html)