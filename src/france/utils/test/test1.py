#!/usr/bin/env python
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np
import subprocess

# Generate svg file ----------

f=plt.figure(figsize=(3,3))
ax=f.add_subplot(111,frameon=False)
theta = np.linspace(0,2*np.pi,10)
ax.plot( np.cos(theta), np.sin(theta), 'b-', lw=2, )
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlim(-1.1,1.1)
ax.set_ylim(-1.1,1.1)
f.savefig('circle1.svg')

# Generate second svg file ----------

f=plt.figure(figsize=(3,3))
ax=f.add_subplot(111,frameon=False)
theta = np.linspace(0,2*np.pi,10)
ax.plot( np.cos(theta), np.sin(theta), 'b-', lw=2)
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlim(-1.1,1.1)
ax.set_ylim(-1.1,1.1)
f.savefig('circle2.svg')

# check output
subprocess.check_call(
    'xmllint --valid --nowarning --noout circle1.svg',
    shell=True)

# check output
subprocess.check_call(
    'xmllint --valid --nowarning --noout circle2.svg',
    shell=True)

if 0:
    print 'done checking circle.svg'
    for i in range(20):
        print

# stack two files
subprocess.check_call(
    'svg_stack circle1.svg circle2.svg > circles.svg',
    #'svg_stack circle.svg > circles.svg',
    shell=True)

# check output
subprocess.check_call(
    #'xmllint --valid --dtdvalid http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd --nowarning --noout circles.svg',
    'xmllint --valid --nowarning --noout circles.svg',
    shell=True)

# check output
subprocess.check_call(
    'rasterizer circles.svg',
    shell=True)
