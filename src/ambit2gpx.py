import os
import xml.dom.minidom
import math
import getopt
import sys

def radian2degree(radian):
    return radian * 180.0 / math.pi

def childElements(parent):   
    elements = []
    for child in parent.childNodes:
        if child.nodeType != child.ELEMENT_NODE:
            continue
        elements.append(child)
    return elements

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

class AmbitXMLParser(object):
    __root = None
    __outputfile = None
    def __init__(self, xml_node, outputfile):
        assert isinstance(xml_node,xml.dom.Node)
        assert xml_node.nodeType == xml_node.ELEMENT_NODE
        self.__root = xml_node
        self.__outputfile = outputfile

    def __parse_sample(self, sample):
        latitude = None
        longitude = None
        altitude = None
        time = None
        for node in childElements(sample):
            key = node.tagName
            if key == "Latitude":
                latitude = radian2degree(float(node.firstChild.nodeValue))
            if key == "Longitude":
                longitude = radian2degree(float(node.firstChild.nodeValue))
            if key == "UTC":
                time = node.firstChild.nodeValue
            if key == "GPSAltitude":
                altitude = node.firstChild.nodeValue
        if latitude != None and longitude != None:
            print >>self.__outputfile, """
<trkpt lat="{latitude}" lon="{longitude}">
    <ele>{altitude}</ele>
    <time>{time}</time>
</trkpt>
""".format(latitude=latitude, longitude=longitude, altitude=altitude, time=time)
    def __parse_samples(self, samples):
        for node in childElements(samples):
            key = node.tagName
            if key == "sample":
                self.__parse_sample(node)
      
    def execute(self):   
        print >>self.__outputfile,'<?xml version="1.0" encoding="UTF-8" standalone="no" ?>'
        print >>self.__outputfile,"""
<gpx xmlns="http://www.topografix.com/GPX/1/1" creator="ambit2gpx" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
  <trk>
    <trkseg>  
"""              
        root = self.__root
        for node in childElements(root):
            key = node.tagName
            if key == "samples":
                self.__parse_samples(node)
                
        print >>self.__outputfile,"""
    </trkseg>        
  </trk>
</gpx>
"""

def usage():
    print """
ambit2gpx filename
"""

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    output = None
    verbose = False
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"
    # ...
    filename = args[0]
    file = open(filename)
    file.readline() # Skip first line
    filecontents = file.read()
    doc = xml.dom.minidom.parseString('<?xml version="1.0" encoding="utf-8"?><top>'+filecontents+'</top>')
    assert doc != None
    top = doc.getElementsByTagName('top')
    assert len(top) == 1    
    outputfile = open(filename + '.gpx', 'w')
    AmbitXMLParser(top[0], outputfile).execute()
        
if __name__ == "__main__":
    main()
