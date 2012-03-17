# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

#from django.contrib.gis.db import models
#from django.contrib.gis.geos import Point
from django.db import models
import datetime, time, random

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
