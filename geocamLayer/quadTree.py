# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import math

from geocamLayer.models import Feature, QuadTreeCell

MAX_FEATURES_PER_CELL = 10

# beyond zoom MAX_ZOOM - 1, corresponding to cells approximately 1 meter
# in size, all points are considered to be "in the same place" and we
# don't split any further.
MAX_ZOOM = 26


class QuadTree(object):
    def __init__(self):
        self.root = QuadTreeCell.getCellAtIndex((0, 0, 0))

    def addFeature(self, feature):
        self.addFeatureToCell(feature, self.root)

    def addFeatureToCell(self, feature, cell):
        cell.updateStats(feature)

        if cell.isLeaf:
            feature.cell = cell
            feature.save()

            if cell.count >= MAX_FEATURES_PER_CELL and cell.zoom < MAX_ZOOM - 1:
                self.splitCell(cell)
        else:
            self.addFeatureToZoom(feature, cell.zoom + 1)

        cell.save()

    def addFeatureToZoom(self, feature, zoom):
        cell = (QuadTreeCell.getCellAtLonLat
                (zoom, (feature.lng, feature.lat)))
        self.addFeatureToCell(feature, cell)

    def createCell(self, zoom, x, y):
        return QuadTreeCell.objects.create(zoom=zoom, x=x, y=y)

    def splitCell(self, cell):
        cell.isLeaf = False
        for feature in Feature.objects.filter(cell=cell):
            self.addFeatureToZoom(feature, cell.zoom + 1)

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
