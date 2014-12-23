#!/usr/bin/env python
#
# Balofo Games
# www.balofogames.com.br
#
import sys, os, argparse, subprocess
import xml.etree.ElementTree as ET

_version = '%(prog)s v1.0'


parser_args = argparse.ArgumentParser(
    prog='SVG Layers to PNG exporter',
    description='Export layers of SVG to individual PNG files',
    version=_version)
parser_args.add_argument('svgfile', help='SVG file to export images from')
parser_args.add_argument('-i', '--inkscape', dest='inkscapepath', default='inkscape', help='Path to Inkscape executable')
parser_args.add_argument('-w', '--width', dest='width', default='1024', help='Screen width')
parser_args.add_argument('-e', '--extra', dest='extra', default='', help='Extra params passed directly to Inkscape')
parser_args.add_argument('-p', '--prefix', dest='prefix', default='', help='Prefix to use when exporting files')
parser_args.add_argument('-d', '--dir', dest='dir', default='.', help='Path to export files')
parser_args.add_argument('-l', '--layers', dest='layers', default='', nargs='+', help='Export only layers declared explicitaly')
parser_args.add_argument('--verbose', dest='verbose', action='store_true', default=False, help='Show more information while exporting')
args = parser_args.parse_args()
layers = []

TEMP_SVG = '.tmp.svg'
SVG_GROUP = '{http://www.w3.org/2000/svg}g'
SVG_GROUP_MODE = '{http://www.inkscape.org/namespaces/inkscape}groupmode'
SVG_LAYER_LABEL = '{http://www.inkscape.org/namespaces/inkscape}label'
SVG_LAYER_ID = 'id'


def verbose_print(msg):
    if args.verbose:
        print('- ' + msg)


def create_fixed_svg():
    verbose_print('parsing svg file...')
    ET.register_namespace('dc','http://purl.org/dc/elements/1.1/')
    ET.register_namespace('cc','http://creativecommons.org/ns#')
    ET.register_namespace('rdf','http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    ET.register_namespace('svg','http://www.w3.org/2000/svg')
    ET.register_namespace('','http://www.w3.org/2000/svg')
    ET.register_namespace('xlink','http://www.w3.org/1999/xlink')
    ET.register_namespace('solipodi','http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd')
    ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')
    f = ET.parse(args.svgfile)
    for group in f.iter(SVG_GROUP):
        if group.attrib.get(SVG_GROUP_MODE) != 'layer':
            continue
        group.attrib[SVG_LAYER_ID] = group.attrib.get(SVG_LAYER_LABEL)
        if len(args.layers) != 0:
            if group.attrib[SVG_LAYER_ID] in args.layers:
                layers.append(group.attrib.get(SVG_LAYER_LABEL))
        else:
            layers.append(group.attrib.get(SVG_LAYER_LABEL))

    verbose_print('parse ok\nwriting temporary modified svg file...')

    f.write(TEMP_SVG, encoding='utf-8', method='xml', xml_declaration=True)

    verbose_print('exporting layers:')
    for l in layers:
        verbose_print('  ' + l)

def prestep():

    print args.layers

    # check if inkscape path is valid:
    retcode = subprocess.call(args.inkscapepath + " -V", shell=True)
    if retcode != 0:
        print  '''Could not find inkscape command line executable, set --inkscape option accordingly.
    It is usually /usr/bin/inkscape in linux and C:\Progra~1\Inkscape\inkscape.exe in windows.'''
        sys.exit(2)

    if args.dir:
        if not os.path.exists( args.dir ):
            verbose_print('creating output dir ' + args.dir)
            os.makedirs( args.dir )

    create_fixed_svg()


def poststep():
    verbose_print('removing temporary file...')
    if os.path.isfile(TEMP_SVG):
        os.remove(TEMP_SVG)


def export_pngs():
    print("RESULT: %d" % (len(layers)))
    for layer in layers:
        outfile = ''.join([args.dir, args.prefix, layer, '.png' ])
        verbose_print('Exporting layer "' + layer + '" to ' + outfile )

        cmd = args.inkscapepath + ' --without-gui --export-png="' + outfile + '" --export-id-only --export-id="' + layer + '" --export-width='+args.width+' -b="#ffffff" ' + args.extra + ' ' + TEMP_SVG
        verbose_print( cmd )
        subprocess.call( cmd, shell=True )

prestep()
export_pngs()
poststep()
