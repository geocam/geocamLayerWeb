#!/usr/bin/env python
from django.core.management.base import BaseCommand, CommandError
from geocamLayer import models
from django.conf import settings
import os, os.path, math

try: import cPickle as pickle
except ImportError: import pickle

CELLS_PER_TILE = 10

class Command(BaseCommand):
    args = ""
    help = "This command restructures the json data"

    def handle(self, *args, **options):
        self.stdout.write("Getting all objects...\n")
        features = models.BaseFeature.objects.all()
        self.stdout.write("%s objects in total\n" % len(features))
        root = os.path.join(settings.MEDIA_ROOT, "tiles")
        tiles = {}
        self.stdout.write("Clustering...\n")
        for point in features:
            lng,lat = point.getPosition()
            for zoom in xrange(10):
                xf = float(lng+180)/(360./(2**(zoom+1)))
                yf = float(lat+ 90)/(360./(2**(zoom+1)))
                xmax = math.floor(xf)
                ymax = math.floor(yf)
                xmin = max(0,xmax-1)
                ymin = max(0,ymax-1)
                xcell = math.floor(((xf-xmax)*CELLS_PER_TILE)*2)
                ycell = math.floor(((yf-ymax)*CELLS_PER_TILE)*2)
                for x in range(int(xmin),int(xmax+1)):
                    tile_path = os.path.join(root, str(zoom), str(x))
                    if not os.path.exists(tile_path):
                        os.makedirs(tile_path)
                    for y in range(int(ymin),int(ymax+1)):
                        tile_file = os.path.join(tile_path, str(y))
                        if tile_file in tiles:
                            tile = tiles[tile_file]
                        elif os.path.exists(tile_file):
                            tile = pickle.load(open(tile_file, 'rb'))
                        else:
                            tile = {}
                        if (xcell,ycell) not in tile:
                            tile[(xcell,ycell)] = []
                        tile[(xcell,ycell)].append(point)
                        tiles[tile_file] = tile
        self.stdout.write("Writing out...\n")
        for tile_path in tiles:
            pickle.dump(tiles[tile_path],open(tile_path,'wb'))
        self.stdout.write("Done.\n")
