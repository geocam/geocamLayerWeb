#!/usr/bin/env python
# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseForbidden, Http404
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext, ugettext_lazy as _
#from django.contrib.gis.geos import Polygon, Point, GeometryCollection
import json

from models import *

DEFAULT_BOUNDS = (180,180,-180,-180)
DEFAULT_START = [0]
DEFAULT_END = [-1]
DEFAULT_CLUSTERING = [0]
DEFAULT_REVERSED = [0]
ENCODINGS = ['geojson', 'kml']
DEFAULT_ENCODING = ["geojson"]

def main(request):
    return HttpResponseRedirect('/static/geojsontest.html')

def points(request, zoom, x, y, objects, encoding=None):
    zoom, x, y = [float(z) for z in [zoom, x, y]]
    south = y - (90/(zoom))
    north = y + (90/(zoom))
    west  = x - (180/(zoom))
    east  = x + (180/(zoom))
    #scale = 360/(2**zoom)
    #south = -90 + scale * y
    #west = -180 + scale * x
    #north = south + scale
    #east = west + scale
    return get(request, west, south, east, north, objects, encoding)

def get(request, west, south, east, north, objects, encoding=None):
    # get parameters from request
    while west < -180: west += 180; east += 180
    while west >  180: west -= 180; east -= 180
    while east < -180: east += 180; east += 180
    while east >  180: east -= 180; east -= 180
    if east < west: inverse = True
    else: inverse = False
    params = dict(request.GET)

    start    = int(params.get(u'start',    DEFAULT_START)[0])
    end      = int(params.get(u'end',      DEFAULT_END)[0])
    cluster  = int(params.get(u'cluster',  DEFAULT_CLUSTERING)[0])
    reverse  = int(params.get(u'reversed', DEFAULT_REVERSED)[0])
    encoding =     params.get(u'encoding', DEFAULT_ENCODING)[0]

    # now for the filtering part
    if inverse: bbox_width = (east-west)*1.2
    else: bbox_width  = (west-east)*1.2
    bbox_height = (south-north)*1.2
    if int(reverse):
        new_objects = reversed(objects)
    else:
        new_objects = objects
    if int(cluster):
        clusters = [[[] for x in range(10)] for y in range(10)]
        for object in new_objects:
            obj_x = object.getPosition()[0]
            obj_y = object.getPosition()[1]
            if not inverse:
                x_pos = int( ((obj_x-east) /bbox_width) *10)
                y_pos = int( ((obj_y-north)/bbox_height) *10)
                if x_pos >= 10 or y_pos >= 10: continue
                if x_pos < 0 or y_pos < 0: continue
                clusters[x_pos][y_pos].append(object)
            else:
                if obj_x < east: obj_x += 360
                x_pos = int( ((obj_x-east) /(bbox_width+360)) *10)
                y_pos = int( ((obj_y-north)/bbox_height)      *10)
                if x_pos >= 10 or y_pos >= 10: continue
                if x_pos < 0 or y_pos < 0: continue
                clusters[x_pos][y_pos].append(object)
 
    else:
        clusters = [[[point]] for point in new_objects]
    clusters = clusters[int(start):]
    if end is not None:
        clusters = clusters[:int(end)-start]

    # and now for the encoding part
    if encoding == 'geojson':
        data = {'type': 'FeatureCollection',
                'features': []}
        print len(clusters)
        for row in clusters:
            for cluster in row:
                lat_coords = [point.getPosition()[1] for point in cluster]
                lng_coords = [point.getPosition()[0] for point in cluster]
                if not len(lat_coords) or not len(lng_coords): continue
                average = [sum(lat_coords)/float(len(lat_coords)),
                           sum(lng_coords)/float(len(lng_coords))]
                east = min(lng_coords); west = max(lng_coords)
                north = min(lat_coords); south = max(lat_coords)
                bbox = [north, east, south, west]

                cluster_data = {'type': 'Feature',
                                'geometry': {
                        'type': 'Point',
                        'coordinates': [average]}
                                }

                if len(cluster) == 1:
                    point = cluster[0]
                    cluster_data['properties'] = {
                        'subtype'    : 'point',
                        'timestamp'  : str(point.getTimeStamp()),
                        'timespan'   : str(point.getTimeSpan()),
                        'name'       : point.getName(),
                        'description': point.getDescriptionHTML()}

                    point_properties = point.getProperties()
                    for property in point.getProperties():
                        cluster_data['properties'] = point_properties['property']

                else:
                    cluster_data['properties'] = {
                        'subtype'   : 'cluster',
                        'numpoints' : len(cluster),
                        'bbox'      : bbox}
                data['features'].append(cluster_data)

        response_data = json.dumps(data, indent=4, sort_keys=True)

    if encoding == 'kml':
        response_data = '<?xml version="1.0" encoding = "UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
        for row in clusters:
            for cluster in row:
                lat_coords = [point.getPosition()[1] for point in cluster]
                lng_coords = [point.getPosition()[0] for point in cluster]
                if not len(lat_coords) or not len(lng_coords): continue
                response_data += '\n<Placemark>'
                average = [sum(lat_coords)/float(len(lat_coords)),
                           sum(lng_coords)/float(len(lng_coords))]
                
                response_data += '\n<Point><coordinates>%s,%s,0</coordinates></Point><ExtendedData>' % (average[0], average[1])
                if len(cluster) > 1:
                    east, north, west, south = GeometryCollection(*[x.getPosition() for x in cluster]).extent
                    bbox = [north, east, south, west]
                    response_data += '\n<Data name="subtype"><value>cluster</value></Data>'
                    response_data += '\n<Data name="numpoints"><value>%s</value></Data>' % len(cluster)
                    response_data += '\n<Data name="bbox"><value>%s</value></Data>' % json.dumps(bbox)
                else:
                    point = cluster[0]
                    response_data += '\n<Data name="subtype"><value>point</value></Data>'
                    info = {'timestamp':point.getTimeStamp(),
                            'timespan': str(point.getTimeSpan()),
                            'name':     point.getName(),
                            'description': point.getDescriptionHTML()}
                    properties = point.getProperties()
                    for property in properties:
                        info[property] = properties[property]
                    for peice in info:
                        response_data += '\n<Data name="%s"><value>%s</value></Data>' % (peice, info[peice])
                response_data += '\n</ExtendedData></Placemark>'
        response_data += '\n</Document></kml>'
                            
    # now return everything
    return HttpResponse(response_data)
