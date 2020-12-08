#!/usr/bin/env python

import subprocess

# "stack" a single Inkscape file
subprocess.check_call(
    'svg_stack arrow.svg > arrow-copy.svg',
    shell=True)

# Inkscape files don't pass xmllint -- don't test

print 'You should manually verify that arrow.svg looks exactly the same as arrow-copy.svg'

subprocess.check_call(
    'rasterizer  arrow-copy.svg',
    shell=True)
