# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import datetime
import time
import random
import math

from django.db import models


class BaseFeature(models.Model):
    # demo feature model demonstrating
    # what you need to implement
    class Meta:
        abstract = True

    def getPosition(self):
        # in as tuple
        return (0,0)
    def getTimeStamp(self):
        # in a time.time() format
        # optional
        return time.time()
    def getTimeSpan(self):
        # in a datetime.timedelta() format
        # optional
        return datetime.timedelta()
    def getName(self):
        # string
        return ""
    def getProperties(self):
        # dict format with name:value
        # optional
        return {}
    def getDescriptionHTML(self):
        # short html with description of object
        return ""

class Feature(BaseFeature):
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    timespan = models.FloatField(null=True, blank=True)
    name = models.CharField(max_length=80)
    description = models.TextField()
    cell = models.ForeignKey('QuadTreeCell', null=True, blank=True)

    def __unicode__(self):
        return u'Feature "%s" (%.6f, %.6f)' % (self.name, self.lng, self.lat)

    @staticmethod
    def randomFeature():
        feature = Feature()
        feature.lat = random.randint(-180,180)
        feature.lng = random.randint(-90,90)
        feature.timestamp = datetime.datetime.now()
        feature.timespan = random.randint(0,3)
        feature.name = "Random Feature"
        feature.description = "Random Feature"
        return feature
        
    def getPosition(self): return (self.lng,self.lat)
    def getTimeStamp(self): return self.timestamp
    def getTimeSpan(self): return self.timespan
    def getName(self): return self.name
    def getDescriptionHTML(self): return self.description
    def getProperties(self): return {} # self.properties

class QuadTreeCell(models.Model):
    zoom = models.PositiveIntegerField()
    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()
    count = models.PositiveIntegerField(default=0)
    isLeaf = models.BooleanField(default=True)
    # centroid: lng, lat
    lng = models.FloatField(default=0.0)
    lat = models.FloatField(default=0.0)
    # bbox: west, south, east, north
    west = models.FloatField(null=True, blank=True)
    south = models.FloatField(null=True, blank=True)
    east = models.FloatField(null=True, blank=True)
    north = models.FloatField(null=True, blank=True)
    # many-to-many for features
    features = models.ManyToManyField("Feature")
    # primary key because we need one
    pkey = models.FloatField(primary_key=True)

    class Meta:
        ordering = ('zoom', 'x', 'y')

    def __unicode__(self):
        return u'QuadTreeCell (%d, %d, %d) count=%d' % (self.zoom, self.x, self.y, self.count)

    @staticmethod
    def getSizeForZoom(zoom):
        return 360.0 / (2.0 ** zoom)

    @staticmethod
    def getIndexAtLonLat(zoom, lonLat):
        size = QuadTreeCell.getSizeForZoom(zoom)
        lng, lat = lonLat
        x = int((lng - (-180)) / size)
        y = int((lat - (-90)) / size)
        return (zoom, x, y)

    @staticmethod
    def getCellAtIndex(coords):
        zoom, x, y = coords
        cell, _created = QuadTreeCell.objects.get_or_create(zoom=zoom, x=x, y=y, pkey=random.random())
        return cell

    @staticmethod
    def getCellAtLonLat(zoom, lonLat):
        return (QuadTreeCell.getCellAtIndex
                (QuadTreeCell.getIndexAtLonLat(zoom, lonLat)))

    def getSize(self):
        return QuadTreeCell.getSizeForZoom(self.zoom)

    def getMinCorner(self):
        size = self.getSize()
        return (-180 + self.x * size,
                -90 + self.y * size)

    def getBounds(self):
        size = self.getSize()
        west, south = self.getMinCorner()
        return (west, south, west + size, south + size)

    def updateStats(self, feature):
        self.lng = (self.count * self.lng + feature.lng) / (self.count + 1)
        self.lat = (self.count * self.lat + feature.lat) / (self.count + 1)

        if self.count:
            self.west = min(self.west, feature.lng)
            self.south = min(self.south, feature.lat)
            self.east = max(self.east, feature.lng)
            self.north = max(self.north, feature.lat)
        else:
            self.west = feature.lng
            self.south = feature.lat
            self.east = feature.lng
            self.north = feature.lat

        self.count += 1
        self.features.add(feature)

    def getDiameter(self):
        if self.count:
            dx = self.east - self.west
            dy = self.north - self.south
            return math.sqrt(dx**2 + dy**2)
        else:
            return 0

__all__ = ['BaseFeature','Feature','QuadTreeCell']
