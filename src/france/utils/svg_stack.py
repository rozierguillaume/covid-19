#!/usr/bin/env python

## Copyright (c) 2009 Andrew D. Straw

## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:

## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
## THE SOFTWARE.

from lxml import etree # Ubuntu Karmic package: python-lxml
import sys, re, os
import base64
from optparse import OptionParser

VERSION = '0.0.2' # keep in sync with setup.py

UNITS = ['pt','px','in','mm','cm']
PT2IN = 1.0/72.0
IN2PT = 72.0
MM2PT = 72.0/25.4
CM2PT = 72.0/2.54
PT2PX = 1.25
PX2PT = 1.0/1.25

relIRI_re = re.compile(r'url\(#(.*)\)')

def get_unit_attr(value):
    # coordinate handling from http://www.w3.org/TR/SVG11/coords.html#Units
    units = None # default (user)
    for unit_name in UNITS:
        if value.endswith(unit_name):
            units = unit_name
            value = value[:-len(unit_name)]
            break
    val_float = float(value) # this will fail if units str not parsed
    return val_float, units

def convert_to_pixels( val, units):
    if units == 'px' or units is None:
        val_px = val
    elif units == 'pt':
        val_px = val*PT2PX
    elif units == 'in':
        val_px = val*IN2PT*PT2PX
    elif units == 'mm':
        val_px = val*MM2PT*PT2PX
    elif units == 'cm':
        val_px = val*CM2PT*PT2PX
    else:
        raise ValueError('unsupport unit conversion to pixels: %s'%units)
    return val_px

def fix_ids( elem, prefix, level=0 ):
    ns = '{http://www.w3.org/2000/svg}'

    if isinstance(elem.tag,basestring) and elem.tag.startswith(ns):

        tag = elem.tag[len(ns):]

        if 'id' in elem.attrib:
            elem.attrib['id'] = prefix + elem.attrib['id']

        # fix references (See http://www.w3.org/TR/SVGTiny12/linking.html#IRIReference )

        for attrib in elem.attrib.keys():
            value = elem.attrib.get(attrib,None)

            if value is not None:

                if attrib.startswith('{http://www.w3.org/1999/xlink}'):
                    relIRI = False
                else:
                    relIRI = True

                if (not relIRI) and value.startswith('#'): # local IRI, change
                    iri = value[1:]
                    value = '#' + prefix + iri
                    elem.attrib[attrib] = value
                elif relIRI:
                    newvalue = re.sub( relIRI_re, r'url(#'+prefix+r'\1)', value)
                    if newvalue != value:
                        elem.attrib[attrib] = newvalue

        # Do same for children

    for child in elem:
        fix_ids(child,prefix,level=level+1)

def export_images( elem, filename_fmt='image%03d', start_idx=1 ):
    """replace inline images with files"""
    ns = '{http://www.w3.org/2000/svg}'
    href = '{http://www.w3.org/1999/xlink}href'
    count = 0
    if isinstance(elem.tag,basestring) and elem.tag.startswith(ns):
        tag = elem.tag[len(ns):]
        if tag=='image':
            buf = etree.tostring(elem,pretty_print=True)
            im_data = elem.attrib[href]
            exts = ['png','jpeg']
            found = False
            for ext in exts:
                prefix = 'data:image/'+ext+';base64,'
                if im_data.startswith(prefix):
                    data_base64 = im_data[len(prefix):]
                    found = True
                    break
            if not found:
                raise NotImplementedError('image found but not supported')

            # decode data
            data = base64.b64decode(data_base64)

            # save data
            idx = start_idx + count
            fname = filename_fmt%idx + '.' + ext
            if os.path.exists(fname):
                raise RuntimeError('File exists: %r'%fname)
            with open(fname,mode='w') as fd:
                fd.write( data )

            # replace element with link
            elem.attrib[href] = fname
            count += 1

    # Do same for children
    for child in elem:
        count += export_images(child, filename_fmt=filename_fmt,
                               start_idx=(start_idx+count) )
    return count

header_str = """<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
 "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<!-- Created with svg_stack (http://github.com/astraw/svg_stack) -->
"""

# ------------------------------------------------------------------
class Document(object):
    def __init__(self):
        self._layout = None
    def setLayout(self,layout):
        self._layout = layout
    def save(self,fileobj,debug_boxes=False,**kwargs):
        if self._layout is None:
            raise ValueError('No layout, cannot save.')
        accum = LayoutAccumulator(**kwargs)
        self._layout.render(accum,debug_boxes=debug_boxes)

        import io
        try:
            file_types = (file, io.IOBase)

        except NameError:
            file_types = (io.IOBase,)

        if isinstance(fileobj, file_types):
            fd = fileobj
            close = False
        else:
            fd = open(fileobj,mode='w')
            close = True
        buf = accum.tostring(pretty_print=True)

        fd.write(header_str)
        fd.write( buf )
        if close:
            fd.close()

class SVGFileBase(object):
    def __init__(self,fname):
        self._fname = fname
        self._root = etree.parse(fname).getroot()
        if self._root.tag != '{http://www.w3.org/2000/svg}svg':
            raise ValueError('expected file to have root element <svg:svg>')

        height, height_units = get_unit_attr(self._root.get('height'))
        width, width_units = get_unit_attr(self._root.get('width'))
        self._width_px = convert_to_pixels( width, width_units)
        self._height_px = convert_to_pixels( height, height_units)
        self._orig_width_px = self._width_px
        self._orig_height_px = self._height_px
        self._coord = None # unassigned

    def get_root(self):
        return self._root

    def get_size(self,min_size=None,box_align=None,level=None):
        return Size(self._width_px,self._height_px)

    def _set_size(self,size):
        self._width_px = size.width
        self._height_px = size.height

    def _set_coord(self,coord):
        self._coord = coord

    def export_images(self,*args,**kwargs):
        export_images(self._root,*args,**kwargs)

class SVGFile(SVGFileBase):
    def __str__(self):
        return 'SVGFile(%s)'%repr(self._fname)

class SVGFileNoLayout(SVGFileBase):
    def __init__(self,fname,x=0,y=0):
        self._x_offset = x
        self._y_offset = y
        super(SVGFileNoLayout,self).__init__(fname)

    def _set_coord(self,coord):
        self._coord = (coord[0] + self._x_offset,
                       coord[1] + self._y_offset )

    def __str__(self):
        return 'SVGFileNoLayout(%s)'%repr(self._fname)

class LayoutAccumulator(object):
    def __init__(self):
        self._svgfiles = []
        self._svgfiles_no_layout = []
        self._raw_elements = []

    def add_svg_file(self,svgfile):
        assert isinstance(svgfile,SVGFile)
        if svgfile in self._svgfiles:
            raise ValueError('cannot accumulate SVGFile instance twice')
        self._svgfiles.append( svgfile )

    def add_svg_file_no_layout(self,svgfile):
        assert isinstance(svgfile,SVGFileNoLayout)
        if svgfile in self._svgfiles_no_layout:
            raise ValueError('cannot accumulate SVGFileNoLayout instance twice')
        self._svgfiles_no_layout.append( svgfile )

    def add_raw_element(self,elem):
        self._raw_elements.append( elem )

    def tostring(self, **kwargs):
        root = self._make_finalized_root()
        return etree.tostring(root,**kwargs)

    def _set_size(self,size):
        self._size = size

    def _make_finalized_root(self):
        # get all required namespaces and prefixes
        NSMAP = {None : 'http://www.w3.org/2000/svg',
                 'sodipodi':'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
                 }
        for svgfile in self._svgfiles:
            origelem = svgfile.get_root()
            for key,value in origelem.nsmap.iteritems():
                if key in NSMAP:
                    assert value == NSMAP[key]
                    # Already in namespace dictionary
                    continue
                elif key == 'svg':
                    assert value == NSMAP[None]
                    # svg is the default namespace - don't insert again.
                    continue
                NSMAP[key] = value

        root = etree.Element('{http://www.w3.org/2000/svg}svg',
                             nsmap=NSMAP)

        if 1:
            # inkscape hack
            root_defs = etree.SubElement(root,'{http://www.w3.org/2000/svg}defs')

        root.attrib['version']='1.1'
        fname_num = 0
        do_layout = True
        work_list=[]
        for svgfile in (self._svgfiles):
            work_list.append( (fname_num, do_layout, svgfile) )
            fname_num += 1
        do_layout = False
        for svgfile in (self._svgfiles_no_layout):
            work_list.append( (fname_num, do_layout, svgfile) )
            fname_num += 1
        for (fname_num, do_layout, svgfile) in work_list:
            origelem = svgfile.get_root()

            fix_id_prefix = 'id%d:'%fname_num
            elem = etree.SubElement(root,'{http://www.w3.org/2000/svg}g')
            elem.attrib['id'] = 'id%d'%fname_num

            elem_sz = svgfile.get_size()
            width_px = elem_sz.width
            height_px = elem_sz.height

            # copy svg contents into new group
            for child in origelem:
                if 1:
                    # inkscape hacks
                    if child.tag == '{http://www.w3.org/2000/svg}defs':
                        # copy into root_defs, not into sub-group
                        for subchild in child:
                            fix_ids( subchild, fix_id_prefix )
                            root_defs.append( subchild )
                        continue
                    elif child.tag == '{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}:namedview':
                        # don't copy
                        continue
                    elif child.tag == '{http://www.w3.org/2000/svg}metadata':
                        # don't copy
                        continue
                elem.append(child)

            fix_ids( elem, fix_id_prefix )

            translate_x = svgfile._coord[0]
            translate_y = svgfile._coord[1]
            if do_layout:
                if svgfile._orig_width_px != width_px:
                    raise NotImplementedError('rescaling width not implemented '
                                              '(hint: set alignment on file %s)'%(
                        svgfile,))
                if svgfile._orig_height_px != height_px:
                    raise NotImplementedError('rescaling height not implemented '
                                              '(hint: set alignment on file %s)'%(
                        svgfile,))
            orig_viewBox = origelem.get('viewBox')
            if orig_viewBox is not None:
                # split by comma or whitespace
                vb_tup = orig_viewBox.split(',')
                vb_tup = [c.strip() for c in vb_tup]
                if len(vb_tup)==1:
                    # not separated by commas
                    vb_tup = orig_viewBox.split()
                assert len(vb_tup)==4
                vb_tup = [float(v) for v in vb_tup]
                vbminx, vbminy, vbwidth, vbheight = vb_tup
                sx = width_px / vbwidth
                sy = height_px / vbheight
                tx = translate_x - vbminx
                ty = translate_y - vbminy
                elem.attrib['transform'] = 'matrix(%s,0,0,%s,%s,%s)'%(
                    sx,sy,tx,ty)
            else:
                elem.attrib['transform'] = 'translate(%s,%s)'%(
                    translate_x, translate_y)
            root.append( elem )
        for elem in self._raw_elements:
            root.append(elem)

        root.attrib["width"] = repr(self._size.width)
        root.attrib["height"] = repr(self._size.height)

        return root

# ------------------------------------------------------------------
class Size(object):
    def __init__(self, width=0, height=0):
        self.width=width
        self.height=height

# directions for BoxLayout
LeftToRight = 'LeftToRight'
RightToLeft = 'RightToLeft'
TopToBottom = 'TopToBottom'
BottomToTop = 'BottomToTop'

# alignment values
AlignLeft = 0x01
AlignRight = 0x02
AlignHCenter = 0x04

AlignTop = 0x020
AlignBottom = 0x040
AlignVCenter = 0x080

AlignCenter = AlignHCenter | AlignVCenter

class Layout(object):
    def __init__(self, parent=None):
        if parent is not None:
            raise NotImplementedError('')

class BoxLayout(Layout):
    def __init__(self, direction, parent=None):
        super(BoxLayout,self).__init__(parent=parent)
        self._direction = direction
        self._items = []
        self._contents_margins = 0 # around edge of box
        self._spacing = 0 # between items in box
        self._coord = (0,0) # default
        self._size = None # uncalculated

    def _set_coord(self,coord):
        self._coord = coord

    def render(self,accum, min_size=None, level=0, debug_boxes=0):
        size = self.get_size(min_size=min_size)
        if level==0:
            # set document size if top level
            accum._set_size(size)
        if debug_boxes>0:
            # draw black line around BoxLayout element
            debug_box = etree.Element('{http://www.w3.org/2000/svg}rect')
            debug_box.attrib['style']=(
                'fill: none; stroke: black; stroke-width: 2.000000;')
            sz=size
            debug_box.attrib['x']=repr(self._coord[0])
            debug_box.attrib['y']=repr(self._coord[1])
            debug_box.attrib['width']=repr(sz.width)
            debug_box.attrib['height']=repr(sz.height)
            accum.add_raw_element(debug_box)

        for (item,stretch,alignment,xml) in self._items:
            if isinstance( item, SVGFile ):
                accum.add_svg_file(item)

                if debug_boxes>0:
                    # draw red line around SVG file
                    debug_box= etree.Element('{http://www.w3.org/2000/svg}rect')
                    debug_box.attrib['style']=(
                        'fill: none; stroke: red; stroke-width: 1.000000;')
                    sz=item.get_size()
                    debug_box.attrib['x']=repr(item._coord[0])
                    debug_box.attrib['y']=repr(item._coord[1])
                    debug_box.attrib['width']=repr(sz.width)
                    debug_box.attrib['height']=repr(sz.height)
                    accum.add_raw_element(debug_box)
            elif isinstance( item, SVGFileNoLayout ):
                accum.add_svg_file_no_layout(item)

                if debug_boxes>0:
                    # draw green line around SVG file
                    debug_box= etree.Element('{http://www.w3.org/2000/svg}rect')
                    debug_box.attrib['style']=(
                        'fill: none; stroke: green; stroke-width: 1.000000;')
                    sz=item.get_size()
                    debug_box.attrib['x']=repr(item._coord[0])
                    debug_box.attrib['y']=repr(item._coord[1])
                    debug_box.attrib['width']=repr(sz.width)
                    debug_box.attrib['height']=repr(sz.height)
                    accum.add_raw_element(debug_box)

            elif isinstance( item, BoxLayout ):
                item.render( accum, min_size=item._size, level=level+1,
                             debug_boxes=debug_boxes)
            else:
                raise NotImplementedError(
                    "don't know how to accumulate item %s"%item)

            if xml is not None:
                extra = etree.Element('{http://www.w3.org/2000/svg}g')
                extra.attrib['transform'] = 'translate(%s,%s)'%(
                    repr(item._coord[0]),repr(item._coord[1]))
                extra.append(xml)
                accum.add_raw_element(extra)

    def get_size(self, min_size=None, box_align=0, level=0 ):
        cum_dim = 0 # size along layout direction
        max_orth_dim = 0 # size along other direction

        if min_size is None:
            min_size = Size(0,0)

        # Step 1: calculate required size along self._direction
        if self._direction in [LeftToRight, RightToLeft]:
            max_orth_dim = min_size.height
            dim_min_size = Size(width=0,
                                height=max_orth_dim)
        else:
            max_orth_dim = min_size.width
            dim_min_size = Size(width=max_orth_dim,
                                height=0)

        cum_dim += self._contents_margins # first margin
        item_sizes = []
        for item_number,(item,stretch,alignment,xml) in enumerate(self._items):
            if isinstance(item,SVGFileNoLayout):
                item_size = Size(0,0)
            else:
                item_size = item.get_size(min_size=dim_min_size, box_align=alignment,level=level+1)
            item_sizes.append( item_size )

            if isinstance(item,SVGFileNoLayout):
                # no layout for this file
                continue

            if self._direction in [LeftToRight, RightToLeft]:
                cum_dim += item_size.width
                max_orth_dim = max(max_orth_dim,item_size.height)
            else:
                cum_dim += item_size.height
                max_orth_dim = max(max_orth_dim,item_size.width)

            if (item_number+1) < len(self._items):
                cum_dim += self._spacing # space between elements
        cum_dim += self._contents_margins # last margin
        orth_dim = max_orth_dim # value without adding margins
        max_orth_dim += 2*self._contents_margins # margins

        # ---------------------------------

        # Step 2: another pass in which expansion takes place
        total_stretch = 0
        for item,stretch,alignment,xml in self._items:
            total_stretch += stretch
        if (self._direction in [LeftToRight, RightToLeft]):
            dim_unfilled_length = max(0,min_size.width - cum_dim)
        else:
            dim_unfilled_length = max(0,min_size.height - cum_dim)

        stretch_hack = False
        if dim_unfilled_length > 0:
            if total_stretch == 0:
                # BoxLayout in which stretch is 0, but unfilled space
                # exists.

                # XXX TODO: what is Qt policy in this case?
                stretch_hack = True
                stretch_inc = 0
            else:
                stretch_inc = dim_unfilled_length / float(total_stretch)
        else:
            stretch_inc = 0

        cum_dim = 0 # size along layout direction
        cum_dim += self._contents_margins # first margin
        is_last_item = False
        for i,(_item,old_item_size) in enumerate(zip(self._items,item_sizes)):
            if (i+1) >= len(self._items):
                is_last_item=True
            (item,stretch,alignment,xml) = _item
            if (self._direction in [LeftToRight, RightToLeft]):
                new_dim_length = old_item_size.width + stretch*stretch_inc
                if stretch_hack and is_last_item:
                    new_dim_length = old_item_size.width + dim_unfilled_length
                new_item_size = Size( new_dim_length, orth_dim )
            else:
                new_dim_length = old_item_size.height + stretch*stretch_inc
                if stretch_hack and is_last_item:
                    new_dim_length = old_item_size.width + dim_unfilled_length
                new_item_size = Size( orth_dim, new_dim_length )

            if isinstance(item,SVGFileNoLayout):
                item_size = Size(0,0)
            else:
                item_size = item.get_size(min_size=new_item_size, box_align=alignment,level=level+1)
            if self._direction == LeftToRight:
                child_box_coord = (cum_dim, self._contents_margins)
            elif self._direction == TopToBottom:
                child_box_coord = (self._contents_margins, cum_dim)
            else:
                raise NotImplementedError(
                    'direction %s not implemented'%self._direction)
            child_box_coord = (child_box_coord[0] + self._coord[0],
                               child_box_coord[1] + self._coord[1])
            child_box_size = new_item_size

            item_pos, final_item_size = self._calc_box( child_box_coord, child_box_size,
                                                        item_size,
                                                        alignment )
            item._set_coord( item_pos )
            item._set_size( final_item_size )

            if self._direction in [LeftToRight, RightToLeft]:
                # Use requested item size so ill behaved item doesn't
                # screw up layout.
                cum_dim += new_item_size.width
            else:
                # Use requested item size so ill behaved item doesn't
                # screw up layout.
                cum_dim += new_item_size.height

            if not is_last_item:
                cum_dim += self._spacing # space between elements
        cum_dim += self._contents_margins # last margin

        # ---------------------------------

        # Step 3: calculate coordinates of each item

        if self._direction in [LeftToRight, RightToLeft]:
            size = Size(cum_dim, max_orth_dim)
        else:
            size = Size(max_orth_dim, cum_dim)

        self._size = size
        return size

    def _calc_box(self, in_pos, in_sz, item_sz, alignment):
        if (AlignLeft & alignment):
            left = in_pos[0]
            width = item_sz.width
        elif (AlignRight & alignment):
            left = in_pos[0]+in_sz.width-item_sz.width
            width = item_sz.width
        elif (AlignHCenter & alignment):
            left = in_pos[0]+0.5*(in_sz.width-item_sz.width)
            width = item_sz.width
        else:
            # expand
            left = in_pos[0]
            width = in_sz.width

        if (AlignTop & alignment):
            top = in_pos[1]
            height = item_sz.height
        elif (AlignBottom & alignment):
            top = in_pos[1]+in_sz.height-item_sz.height
            height = item_sz.height
        elif (AlignVCenter & alignment):
            top = in_pos[1]+0.5*(in_sz.height-item_sz.height)
            height = item_sz.height
        else:
            # expand
            top = in_pos[1]
            height = in_sz.height

        pos = (left,top)
        size = Size(width,height)
        return pos,size

    def _set_size(self, size):
        self._size = size

    def setSpacing(self,spacing):
        self._spacing = spacing

    def addSVG(self, svg_file, stretch=0, alignment=0, xml=None):
        if not isinstance(svg_file,SVGFile):
            svg_file = SVGFile(svg_file)
        if xml is not None:
            xml = etree.XML(xml)
        self._items.append((svg_file,stretch,alignment,xml))

    def addSVGNoLayout(self, svg_file, x=0, y=0, xml=None):
        if not isinstance(svg_file,SVGFileNoLayout):
            svg_file = SVGFileNoLayout(svg_file,x=x,y=y)
        stretch=0
        alignment=0
        if xml is not None:
            xml = etree.XML(xml)
        self._items.append((svg_file,stretch,alignment,xml))

    def addLayout(self, layout, stretch=0):
        assert isinstance(layout,Layout)
        alignment=0 # always expand a layout
        xml=None
        self._items.append((layout,stretch,alignment,xml))

class HBoxLayout(BoxLayout):
    def __init__(self, parent=None):
        super(HBoxLayout,self).__init__(LeftToRight,parent=parent)

class VBoxLayout(BoxLayout):
    def __init__(self, parent=None):
        super(VBoxLayout,self).__init__(TopToBottom,parent=parent)

# ------------------------------------------------------------------

def main():
    usage = '''%prog FILE1 [FILE2] [...] [options]

concatenate SVG files

This will concatenate FILE1, FILE2, ... to a new svg file printed to
stdout.

'''

    parser = OptionParser(usage, version=VERSION)
    parser.add_option("--margin",type='str',
                      help='size of margin (in any units, px default)',
                      default=None)
    parser.add_option("--direction",type='str',
                      default='vertical',
                      help='horizontal or vertical (or h or v)')
    (options, args) = parser.parse_args()
    fnames = args

    if options.direction.lower().startswith('v'):
        direction = 'vertical'
    elif options.direction.lower().startswith('h'):
        direction = 'horizontal'
    else:
        raise ValueError('unknown direction %s'%options.direction)

    if options.margin is not None:
        margin_px = convert_to_pixels(*get_unit_attr(options.margin))
    else:
        margin_px = 0

    if 0:
        fd = open('tmp.svg',mode='w')
    else:
        fd = sys.stdout

    doc = Document()
    if direction == 'vertical':
        layout = VBoxLayout()
    elif direction == 'horizontal':
        layout = HBoxLayout()

    for fname in fnames:
        layout.addSVG(fname,alignment=AlignCenter)

    layout.setSpacing(margin_px)
    doc.setLayout(layout)
    doc.save( fd )

if __name__=='__main__':
    main()
