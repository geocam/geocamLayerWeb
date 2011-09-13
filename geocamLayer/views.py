# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.gis.geos import Polygon, Point, GeometryCollection
import json

DEFAULT_BOUNDS = None
DEFAULT_START = 0
DEFAULT_END = None
DEFAULT_CLUSTERING = 0
DEFAULT_REVERSED = 0
ENCODINGS = ['geojson', 'kml']
DEFAULT_ENCODING = "geojson"

def get(request, objects, encoding=None):
    # get parameters from request
    params = dict(request.GET)
    if u'bbox' in params:
        bounds = Polygon.from_bbox(params[u'bbox'][0].split(','))
        distance = Point([float(x) for x in params[u'bbox'][0].split(',')[:2]]).distance(Point([float(x) for x in params[u'bbox'][0].split(',')[2:]]))/10
    else: bounds = DEFAULT_BOUNDS
    if u'start' in params: start = params[u'start'][0]
    else: start = DEFAULT_START
    if u'end' in params: end = params[u'end'][0]
    else: end = DEFAULT_END
    if u'cluster' in params: cluster = params[u'cluster'][0]
    else: cluster = DEFAULT_CLUSTERING
    if u'reversed' in params: reverse = params[u'reversed'][0]
    else: reverse = DEFAULT_REVERSED
    if u'encoding' in params: encoding = params[u'encoding'][0]
    else: encoding = DEFAULT_ENCODING
    
    # now for the filtering part
    new_objects = []
    if bounds:
        for object in objects:
            if bounds.prepared.contains(object.getPosition()): new_objects.append(object)
    else: new_objects = list(objects)
    new_objects.sort(key=lambda x: x.getTimeStamp())
    if int(reverse): new_objects.reverse()
    if int(cluster):
        clusters = []
        copy = list(new_objects)
        for object in new_objects:
            new_cluster = [x for x in copy if object.getPosition().distance(x.getPosition()) <= distance]
            for x in new_cluster: copy.remove(x)
            clusters.append(new_cluster)
    else:
        clusters = [[x] for x in new_objects]
    clusters = clusters[int(start):]
    if end is not None: clusters = clusters[:int(end)-start]
    
    # and now for the encoding part
    if encoding == 'geojson':
        data = {'type': 'FeatureCollection',
                'features': []}
        for cluster in clusters:
            lat_coords = [x.getPosition().coords[0] for x in cluster]
            lng_coords = [x.getPosition().coords[1] for x in cluster]
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
                    points[coords][str(property)] = point.getProperties()[property]
            bbox = GeometryCollection(*[x.getPosition() for x in cluster]).extent
            cluster_data = {'type': 'Feature',
                            'geometry': {
                    'type': 'Point',
                    'coordinates': [average]},
                            'properties': {
                    'numpoints': len(cluster),
                    'bbox': bbox,
                    'points':points
                    }}
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
                response_data += '<Data name="%s"><value>%s</value></Data>' % (str(point), json.dumps(points[point]))
            response_data += '</ExtendedData></Placemark>'
        response_data += '</Document></kml>'
    
    # now return everything
    return HttpResponse(response_data)
