.PHONY: all run

all: run
install:
	pip install -r requirements.txt

run: install
	python test_main.py
	treevalue graph -t 'test_main.*' -o artifacts/treevalue_graph.gv -T '(This is a title for t1 and t2)'
	potc export -v 'test_main.t*'

clean:
	rm -rf artifacts/*
	touch artifacts/.keep
