.PHONY: all run

all: run
run:
	python test_main.py
	treevalue graph -t 'test_main.*' -o artifacts/test_graph.gv -T '(This is a title for t1 and t2)'

clean:
	rm -rf artifacts/*
	touch artifacts/.keep
