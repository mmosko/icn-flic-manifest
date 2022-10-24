
.PHONY: all reqs

VER=03
BASE=draft-irtf-icnrg-flic
SRC=$(BASE).xml
VERSIONED=$(BASE)-$(VER)
OUTPUT=$(VERSIONED).txt $(VERSIONED).html


all: | venv $(OUTPUT)

%.txt: $(SRC)
	echo "Building TEXT output"
	venv/bin/python3 render.py -i $< -o $@ -f text

%.html: $(SRC)
	echo "Building HTML output"
	venv/bin/python3 render.py -i $< -o $@ -f html

venv:
	python3 -m venv venv
	# If pip does not succeed, remove the venv directory to try again later
	if ! venv/bin/python3 -m pip install -r requirements.txt; then rm -rf venv; fi

