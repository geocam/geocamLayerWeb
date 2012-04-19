#!/usr/bin/env python
from django.core.management.base import BaseCommand, CommandError
from geocamLayer import models
from django.conf import settings
from optparse import make_option
import os, os.path, shutil, math, json, datetime, random

try: import cPickle as pickle
except ImportError: import pickle

CELLS_PER_TILE = 10
NUMBER_ZOOMS = 10

class Cluster(object):
    def __init__(self, finalZoom = False):
        self.numPoints = 0
        self.xSum, self.ySum = 0,0
        self.south = self.west = self.east = self.north = None
        self.points = []
        self.finalZoom = finalZoom

    def add_point(self, point):
        self.numPoints += 1
        if self.numPoints == 1 or self.finalZoom:
            self.points.append(point)
        else:
            self.points = []
        x, y = point.getPosition()
        self.xSum += x
        self.ySum += y
        if self.east is None or x < self.east:
            self.east = x
        if self.west is None or x > self.west:
            self.west = x
        if self.south is None or y > self.south:
            self.south = y
        if self.north is None or y < self.north:
            self.north = y

    def get_json(self):
        data = []
        if self.numPoints > 1 and not self.finalZoom:
            data.append({'type': 'Feature',
                         'geometry': {
                        'type': 'Point',
                        'coordinates': [
                            self.xSum / float(self.numPoints),
                            self.ySum / float(self.numPoints),
                            ],
                        },
                         'properties': {
                        'subtype': 'Cluster',
                        'numPoints': self.numPoints,
                        'bbox': [self.north, self.east, self.south, self.west],
                        }
                         }
                        )

        for point in self.points:
            data.append({'type': 'Feature',
                         'geometry': {
                        'type': 'point',
                        'coordinates': [
                            point.getPosition()[0],
                            point.getPosition()[1],
                            ],
                        },
                         'properties': {
                        'subtype': 'point',
                        'timestamp': str(point.getTimeStamp()),
                        'timespan': str(point.getTimeSpan()),
                        'name': point.getName(),
                        'description': point.getDescriptionHTML()
                        }
                         }
                        )

        return data

class Command(BaseCommand):
    args = ""
    help = "This command restructures the json data"

    option_list = BaseCommand.option_list + (
        make_option('--clear',
                    action="store_true",
                    dest="clear_files",
                    default=False,
                    help="Delete directory structure before writing out (be careful!)"
                    ),
        make_option('--noaa', dest="noaaFile",
                    help="Uses noaa file instead of database",
                    metavar="FILE", default=None),
        )

    root = os.path.join(settings.MEDIA_ROOT, "tiles")
    tiles = {}

    def process_point(self, point):
        lng,lat = point.getPosition()
        for zoom in xrange(NUMBER_ZOOMS):
            # fragment this
            xf = float(lng + 180) / (360. / (2**(zoom+1)))
            yf = float(lat + 90) / (360. / (2**(zoom+1)))
            xmax = math.floor(xf)
            ymax = math.floor(yf)
            xmin = max(0,xmax - 1)
            ymin = max(0,ymax - 1)
            xcell = int(math.floor(((xf - xmax) * CELLS_PER_TILE)))
            ycell = int(math.floor(((yf - ymax) * CELLS_PER_TILE)))
            for x in range(int(xmin),int(xmax+1)):
                tile_path = os.path.join(self.root, str(zoom), str(x))
                if not os.path.exists(tile_path):
                    os.makedirs(tile_path)
                for y in range(int(ymin),int(ymax+1)):
                    tile_file = os.path.join(tile_path, str(y)+'.json')
                    tile = self.tiles.get(tile_file, {})
                    cell = tile.setdefault((xcell,ycell),Cluster(finalZoom=True if zoom == NUMBER_ZOOMS-1 else False))
                    cell.add_point(point)
                    self.tiles[tile_file] = tile

    def write_out(self):
        for tile_file, tile in self.tiles.iteritems():
            clusters = []
            for pos, cluster in tile.iteritems():
                clusters.extend(cluster.get_json())
            data = {'type': 'FeatureCollection',
                    'features': clusters}
            json.dump(data, open(tile_file,'w'), sort_keys=True, indent=4)

    def clear_files(self):
        if os.path.exists(self.root):
            shutil.rmtree(self.root)

    def parseDegrees(self, data, positiveDirection):
        direction = data[-1]
        direction = 1 if direction == positiveDirection else -1
        data = data[:-1]
        fields = [float(x) for x in data.split('-')]
        degrees, minutes = fields[:2]
        val = degrees + minutes / 60.0
        if len(fields) == 3:
            seconds = fields[2]
            val += seconds / 3600.0
        return direction * val

    def parseLatitude(self, latStr):
        return self.parseDegrees(latStr, 'N')

    def parseLongitude(self, latStr):
        return self.parseDegrees(latStr, 'E')

    def get_database_objects(self):
        return models.Feature.objects.all()

    def get_noaa_objects(self, fname):
        assert(os.path.exists(fname))
        features = []

        for line in open(fname):
            data = line.strip().split(';')

            blockNumber, stationNumber, ICAOLocation, placeName,\
                state, countryName, WMORegion, stationLatitude,\
                stationLongitude, upperAirLatitude, upperAirLongitude,\
                stationElevation, upperAirElevation, RBSNIndicator\
                = data
            
            stationLatitude = self.parseLatitude(stationLatitude)
            stationLongitude = self.parseLongitude(stationLongitude)

            feature = models.Feature()
            feature.lat = stationLatitude
            feature.lng = stationLongitude
            feature.timestamp = datetime.datetime.now()
            feature.timespan = random.randint(0,3)
            feature.name = placeName
            feature.description = countryName

            features.append(feature)

        return features

    def handle(self, *args, **options):
        self.stdout.write("Getting all objects...\n")
        if options['noaaFile'] is not None:
            features = self.get_noaa_objects(options['noaaFile'])
        else:
            features = self.get_database_objects()
        self.stdout.write("%s objects in total\n" % len(features))
        if options['clear_files']:
            self.stdout.write("Clearing existing files...\n")
            self.clear_files()
        self.stdout.write("Clustering...\n")
        for point in features:
            self.process_point(point)
        self.stdout.write("Writing out...\n")
        self.write_out()
        self.stdout.write("Done.\n")
