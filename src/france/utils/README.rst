svg_stack - combine multiple SVG elements into a single SVG element
===================================================================

Overview
--------

svg_stack combines multiple SVG elements into a single SVG element. It
can be called from the command line (less flexible) or called from the
Python interface (more flexible).

This tool exists primarily exists to automatically composite SVG files
into a single SVG file that remains compatible with Inkscape_. If
compatibility with Inkscape is not required, one can create an svg
file with multiple, nested <svg> elements. Inkscape, however, doesn't
seem to handle nested <svg> elements particularly well. Thus, this
tool was born.

.. _Inkscape: http://inkscape.org/

Example command line usage
--------------------------

For example, given the files red_ball.svg and blue_triangle.svg::

  svg_stack.py --direction=h --margin=100 red_ball.svg blue_triangle.svg > shapes.svg

will stack them horizontally with a 100 px margin between them. The
result will be in a file called shapes.svg.

Example Python usage
--------------------

A Qt_ like API provides more advanced layout capabilities. For example::

  #!/usr/bin/env python

  import svg_stack as ss

  doc = ss.Document()

  layout1 = ss.HBoxLayout()
  layout1.addSVG('red_ball.svg',alignment=ss.AlignTop|ss.AlignHCenter)
  layout1.addSVG('blue_triangle.svg',alignment=ss.AlignCenter)

  layout2 = ss.VBoxLayout()

  layout2.addSVG('red_ball.svg',alignment=ss.AlignCenter)
  layout2.addSVG('red_ball.svg',alignment=ss.AlignCenter)
  layout2.addSVG('red_ball.svg',alignment=ss.AlignCenter)
  layout1.addLayout(layout2)

  doc.setLayout(layout1)

  doc.save('qt_api_test.svg')

.. _Qt: http://qt.nokia.com/

See also
--------

 * `svg_utils <https://github.com/btel/svg_utils>`_ does a very
   similar thing. (See also a related `blog post
   <http://neuroscience.telenczuk.pl/?p=331>`_.)

Meta-data
---------

 * License: MIT (see source code of svg_stack for full license)
 * Author: Andrew D. Straw
 * Contact: strawman@astraw.com
 * Homepage: http://github.com/astraw/svg_stack
 * Issue tracker: http://github.com/astraw/svg_stack/issues

Command-line usage
------------------

::

  Usage: svg_stack FILE1 [FILE2] [...] [options]

  concatenate SVG files

  This will concatenate FILE1, FILE2, ... to a new svg file printed to
  stdout.



  Options:
    --version             show program's version number and exit
    -h, --help            show this help message and exit
    --margin=MARGIN       size of margin (in any units, px default)
    --direction=DIRECTION
                          horizontal or vertical (or h or v)

