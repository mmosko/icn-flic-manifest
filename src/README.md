# Simplified build system

We now use the IETF web API to render XML to TXT, HTML, and PDF.

You must specify which source version you want to build in the Makefile by
updating the `VER=` line.

You need to manually copy the .txt and .html versions to the ../docs/build directory.
As this directory tracks what is on the IETF datatracker, perhaps we could remove it?
