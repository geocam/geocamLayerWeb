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
from django.contrib.gis.geos import Polygon, Point, GeometryCollection
import json

DEFAULT_BOUNDS = (180,180,-180,-180)
DEFAULT_START = [0]
DEFAULT_END = [-1]
DEFAULT_CLUSTERING = [0]
DEFAULT_REVERSED = [0]
ENCODINGS = ['geojson', 'kml']
DEFAULT_ENCODING = ["geojson"]

def main(request):
    return HttpResponseRedirect('/static/geojsontest.html')

def get(request, objects, encoding=None):
    # get parameters from request
    params = dict(request.GET)
    inverse = False
    if u'bbox' in params:
        values = params[u'bbox'][0].split(',')
        south, west, north, east = [float(x) for x in values]
        if east < west: inverse = True
    else: bounds = DEFAULT_BOUNDS

    start    = int(params.get(u'start',    DEFAULT_START)[0])
    end      = int(params.get(u'end',      DEFAULT_END)[0])
    cluster  = int(params.get(u'cluster',  DEFAULT_CLUSTERING)[0])
    reverse  = int(params.get(u'reversed', DEFAULT_REVERSED)[0])
    encoding =     params.get(u'encoding', DEFAULT_ENCODING)[0]

    # now for the filtering part
    bbox_width  = west-east
    bbox_width_ = bbox_width*1.2 # cheap trick to get clusters to cluster correctly
    bbox_height = south-north
    if int(reverse):
        new_objects = reversed(objects)
    else:
        new_objects = objects
    if int(cluster) and u'bbox' in params:
        clusters = [[[] for x in range(10)] for y in range(10)]
        for object in new_objects:
            obj_x = object.getPosition().coords[0]
            obj_y = object.getPosition().coords[1]
            if not inverse:
                x_pos = int( ((obj_x-east) /bbox_width_) *10)
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
        for row in clusters:
            for cluster in row:
                lat_coords = [point.getPosition().coords[1] for point in cluster]
                lng_coords = [point.getPosition().coords[0] for point in cluster]
                if not len(lat_coords) or not len(lng_coords): continue
                average = [sum(lat_coords)/float(len(lat_coords)),
                           sum(lng_coords)/float(len(lng_coords))]
                east, north, west, south = GeometryCollection(*[point.getPosition() for point in cluster]).extent
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
        for cluster in clusters:
            response_data += '<Placemark>'
            lat_coords = [x.getPosition().coords[1] for x in cluster]
            lng_coords = [x.getPosition().coords[0] for x in cluster]
            average = [sum(lat_coords)/float(len(lat_coords)),
                       sum(lng_coords)/float(len(lng_coords))]
            points = {}
            for point in cluster:
                coords = str(list(reversed(point.getPosition().coords)))
                points[coords] = {'timestamp':point.getTimeStamp(),
                                  'timespan': str(point.getTimeSpan()),
                                  'name':     point.getName(),
                                  'description': point.getDescriptionHTML()}
                for property in point.getProperties():
                    points[coords][property] = point.getProperties()[property]
            bbox = GeometryCollection(*[x.getPosition() for x in cluster]).extent
            bbox = [bbox[1], bbox[0], bbox[3], bbox[2]]
            response_data += '<Point><coordinates>%s,%s,0</coordinates></Point><ExtendedData>' % (average[0], average[1])
            response_data += '<Data name="numpoints"><value>%s</value></Data>' % len(cluster)
            response_data += '<Data name="bbox"><value>%s</value></Data>' % json.dumps(bbox)
            for point in points:
                response_data += '<Data name="%s"><value>%s</value></Data>'% (str(point), json.dumps(points[point]))
            response_data += '</ExtendedData></Placemark>'
        response_data += '</Document></kml>'

    # now return everything
    return HttpResponse(response_data)
