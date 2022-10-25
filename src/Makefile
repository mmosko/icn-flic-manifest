
.PHONY: all reqs

VER=04
BASE=draft-irtf-icnrg-flic
VERSIONED=$(BASE)-$(VER)
OUTPUT=$(VERSIONED).txt $(VERSIONED).html $(VERSIONED).pdf


all: | venv $(OUTPUT)

%.txt: %.xml
	@echo "Building TEXT output"
	venv/bin/python3 render.py -i $< -o $@ -f text

%.html: %.xml
	@echo "Building HTML output"
	venv/bin/python3 render.py -i $< -o $@ -f html

%.pdf: %.xml
	@echo "Building PDF output"
	venv/bin/python3 render.py -i $< -o $@ -f pdf

venv:
	@echo "Creating Python virtual environment"
	@python3 -m venv venv
	# If pip does not succeed, remove the venv directory to try again later
	@if ! venv/bin/python3 -m pip install -r requirements.txt; then rm -rf venv; fi

