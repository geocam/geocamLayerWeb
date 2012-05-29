# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import sys
import math
import random

from django.db import transaction

from geocamLayer.models import Feature, QuadTreeCell

MAX_FEATURES_PER_CELL = 10

# beyond zoom MAX_ZOOM - 1, corresponding to cells approximately 1 meter
# in size, all points are considered to be "in the same place" and we
# don't split any further.
MAX_ZOOM = 26


class QuadTree(object):
    def __init__(self):
        self.cells = {}
        self.features = []
        self.root = self.getCellAtIndex((0, 0, 0))

    def getCellAtIndex(self, index):
        if index in self.cells:
            cell = self.cells[index]
        else:
            zoom, x, y = index
            cell = self.cells.setdefault(index, QuadTreeCell(zoom=zoom, x=x, y=y))
        return cell

    def getCellAtLonLat(self, zoom, lonLat):
        return self.getCellAtIndex(QuadTreeCell.getIndexAtLonLat(zoom, lonLat))

    def addFeature(self, feature):
        self.addFeatureToCell(feature, self.root)

    def addFeatureToCell(self, feature, cell):
        cell.updateStats(feature)

        if cell.isLeaf:
            feature.cell = cell
            self.features.append(feature)
            if not hasattr(cell, 'features'):
                cell.features = []
            cell.features.append(feature)

            if cell.count >= MAX_FEATURES_PER_CELL and cell.zoom < MAX_ZOOM - 1:
                self.splitCell(cell)
        else:
            self.addFeatureToZoom(feature, cell.zoom + 1)

    def addFeatureToZoom(self, feature, zoom):
        cell = (self.getCellAtLonLat
                (zoom, (feature.lng, feature.lat)))
        self.addFeatureToCell(feature, cell)

    def splitCell(self, cell):
        cell.isLeaf = False
        for feature in cell.features:
            self.addFeatureToZoom(feature, cell.zoom + 1)

    @transaction.commit_manually
    def finish(self):
        for cell in self.cells.itervalues():
            cell.save()
            sys.stdout.write('c')
            sys.stdout.flush()
        transaction.commit()
        for feature in self.features:
            feature.save()
            sys.stdout.write('f')
            sys.stdout.flush()
        transaction.commit()

    def debugStats(self):
        print '=== DEBUG STATS ==='
        zoom = 0
        while 1:
            cellsAtZoom = QuadTreeCell.objects.filter(zoom=zoom)
            if not cellsAtZoom:
                break
            numCellsAtZoom = cellsAtZoom.count()
            numFeatures = 0
            diameterSum = 0.0
            for cell in cellsAtZoom:
                numFeatures += cell.count
                diameterSum += cell.getDiameter()
            meanDiameter = diameterSum / numCellsAtZoom
            maxNumCellsAtZoom = math.ceil(0.5 * 4 ** zoom)
            print ('zoom=%d numCells=%d maxNumCells=%d numFeatures=%d meanDiameter=%.1f'
                   % (zoom, numCellsAtZoom, maxNumCellsAtZoom, numFeatures, meanDiameter))
            zoom += 1
