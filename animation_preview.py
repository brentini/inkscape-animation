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
import os
import random
from fltk import *
import subprocess
import xml.etree.ElementTree as ET

# pygame
import pygame
from pygame.locals import Color, KEYUP, K_ESCAPE, K_RETURN
import spritesheet
from sprite_strip_anim import SpriteStripAnim

class Preview(inkex.Effect):
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
        self.OptionParser.add_option('-f', '--framerate', action = 'store',
          type = 'int', dest = 'framerate', default = '1',
          help = 'Current frame number (starts with 1)')

        self.OptionParser.add_option('-w', '--width', action = 'store',
          type = 'int', dest = 'width', default = '550',
          help = 'Exported screen width')

    def effect(self):
        """
        Effect behaviour.
        Overrides base class' method and inserts "Hello World" text into SVG document.
        """
        # Get script's "--frame" option value.
        FPS = self.options.framerate

        # Get access to main SVG document element and get its dimensions.
        svg = self.document.getroot()
        # or alternatively
        # svg = self.document.xpath('//svg:svg',namespaces=inkex.NSS)[0]

        # Again, there are two ways to get the attibutes:
        ratio = float( inkex.unittouu(svg.attrib['height']) / inkex.unittouu(svg.get('width')) )
        W = self.options.width # Default preview width
        H = W * ratio # Default preview height
        width  = int(W)
        height = int(H)

        # Exports spritesheet data
        temp_filepath = self.args[-1]
        commandlineargs = ["python", "svg_layers_to_png_export.py", temp_filepath,"-d","/tmp/","--width",("%d"%(W))]
        p = subprocess.Popen(commandlineargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = p.communicate()[0]   # Fetch pipe output and pass it along
        exitcode = p.wait() # block until thread completes

        # Subprocess call based on
        # http://atramentum.googlecode.com/hg/atramentum.py
        #inkex.debug("Command output (%s): %s " % (exitcode, stdout))

        res = stdout.split('RESULT: ')
        count = int(res.pop())
        #inkex.debug(count)

        # Sprite Animation
        # http://www.pygame.org/wiki/Spritesheet
        surface = pygame.display.set_mode((width,height))
        #FPS = framerate
        frames = FPS / 12
        strips = []

        # Creates the spritesheet
        for i in range(1,count):
            strips.append(SpriteStripAnim(('/tmp/frame-%d.png')%i, (0,0,W,H), 1, 1, True, frames))

        fill = Color("white")
        clock = pygame.time.Clock()
        n = 0
        strips[n].iter()
        image = strips[n].next()
        while True:
            for e in pygame.event.get():
                if e.type == KEYUP:
                    if e.key == K_ESCAPE:
                        sys.exit()
#                    elif e.key == K_RETURN:
            n += 1
            if n >= len(strips):
                n = 0
            strips[n].iter()
            surface.fill(fill)
            surface.blit(image, (0,0))
            pygame.display.flip()
            image = strips[n].next()
            clock.tick(FPS)

# Create effect instance and apply it.
effect = Preview()
effect.affect()
