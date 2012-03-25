#!/usr/bin/env python
from django.core.management.base import BaseCommand, CommandError
from geocamLayer import models
from django.conf import settings
import os, os.path, math, json

try: import cPickle as pickle
except ImportError: import pickle

CELLS_PER_TILE = 10

class Cluster(object):
    def __init__(self):
        self.numPoints = 0
        self.xSum, self.ySum = 0,0
        self.south = self.west = self.east = self.north = None

    def add_point(self, point):
        self.numPoints += 1
        x, y = point.getPosition()
        self.xSum += x
        self.ySum += y
        if self.west is None or x < self.west:
            self.west = x
        if self.east is None or x > self.east:
            self.east = x
        if self.south is None or y < self.south:
            self.south = y
        if self.north is None or y > self.north:
            self.north = y

    def get_json(self):
        return {'type': 'Feature',
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
                    'bbox': [self.west, self.south, self.east, self.north],
                    }
                }


class Command(BaseCommand):
    args = ""
    help = "This command restructures the json data"
    root = os.path.join(settings.MEDIA_ROOT, "tiles")
    tiles = {}

    def process_point(self, point):
        lng,lat = point.getPosition()
        for zoom in xrange(10):
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
                    cell = tile.setdefault((xcell,ycell),Cluster())
                    cell.add_point(point)
                    self.tiles[tile_file] = tile

    def write_out(self):
        for tile_file, tile in self.tiles.iteritems():
            clusters = []
            for pos, cluster in tile.iteritems():
                clusters.append(cluster.get_json())
            data = {'type': 'FeatureCollection',
                    'features': clusters}
            json.dump(data, open(tile_file,'w'), sort_keys=True, indent=4)

    def handle(self, *args, **options):
        self.stdout.write("Getting all objects...\n")
        features = models.Feature.objects.all()
        self.stdout.write("%s objects in total\n" % len(features))
        self.stdout.write("Clustering...\n")
        for point in features:
            self.process_point(point)
        self.stdout.write("Writing out...\n")
        self.write_out()
        self.stdout.write("Done.\n")
