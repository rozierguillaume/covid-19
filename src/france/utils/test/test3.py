#!/usr/bin/env python

import subprocess

# stack two Inkscape generated files
subprocess.check_call(
    'svg_stack --direction=h --margin=100 red_ball.svg blue_triangle.svg > shapes_test.svg',
    shell=True)

# Inkscape files don't pass xmllint -- don't test

print 'You should manually verify that shapes_test.svg looks exactly the same as shapes.svg'

subprocess.check_call(
    'rasterizer shapes_test.svg',
    shell=True)
