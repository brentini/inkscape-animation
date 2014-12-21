#!/usr/bin/env python

'''
The MIT License (MIT)

Copyright (c) 2014 Pedro de Almeida Sacramento

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
sys.path.append('/usr/share/inkscape/extensions')

# We will use the inkex module with the predefined Effect base class.
import inkex
# The simplestyle module provides functions for style parsing.
from simplestyle import *

import random

def rename_layers( self, frame ):
    count = 0
    pathNodes = self.document.xpath('//svg:g',namespaces=inkex.NSS)
    for g in pathNodes:
        if g.get(inkex.addNS('groupmode', 'inkscape')) == 'layer':
            label = ( ("frame-%d") % (count) )
            g.set(inkex.addNS('label', 'inkscape'), label)

            if (frame != count):
                g.set('style', formatStyle( { 'display' : 'none' } ))
            else:
                g.set('style', formatStyle( { 'display' : 'inline' } ))

            count = count+1

    return count

def getLayer(svg, layerName):
    for g in svg.xpath('//svg:g', namespaces=inkex.NSS):
        if g.get(inkex.addNS('groupmode', 'inkscape')) == 'layer' \
            and g.get(inkex.addNS('label', 'inkscape')) \
            == layerName:
            return g

def goto_layer(self,label):
    # Selects current layer
    nv = self.getNamedView()
    nv.set(inkex.addNS('current-layer', 'inkscape'),label)

class Animation(inkex.Effect):
    """
    Inkscape Animation Extension
    """
    def __init__(self):
        """
        Constructor.
        Defines the "--what" option of a script.
        """
        # Call the base class constructor.
        inkex.Effect.__init__(self)

        # Define string option "--frame" with "-f" shortcut and default value "1"
        self.OptionParser.add_option('-f', '--frame', action = 'store',
          type = 'int', dest = 'frame', default = '1',
          help = 'Current frame number (starts with 1)')

    def effect(self):
        """
        Effect behaviour.
        Overrides base class' method and inserts "Hello World" text into SVG document.
        """
        # Get script's "--frame" option value.
        frame = self.options.frame

        # Get access to main SVG document element and get its dimensions.
        svg = self.document.getroot()
        # or alternatively
        # svg = self.document.xpath('//svg:svg',namespaces=inkex.NSS)[0]

        # Again, there are two ways to get the attibutes:
        width  = inkex.unittouu(svg.get('width'))
        height = inkex.unittouu(svg.attrib['height'])

        # Checks if total layers is correct
        total = rename_layers( self, frame )

        #inkex.debug('%s %s' % (frame,total))
        current = ( 'frame-%d' % (frame) )

        # Creates layers
        for i in range(total, frame+1):
            # Create a new layer.
            label = ( 'frame-%d' % (i))
            g = inkex.etree.SubElement(svg, 'g')
            g.set(inkex.addNS('id', ''), label) # TODO: Remove this "dangerous" operation!
            g.set(inkex.addNS('label', 'inkscape'), label)
            g.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
            if (i != frame):
                g.set('style', formatStyle( { 'display' : 'none' } ))
            else:
                g.set('style', formatStyle( { 'display' : 'inline' } ))

        # Selects new created layer
        goto_layer(self, current)

# Create effect instance and apply it.
effect = Animation()
effect.affect()
