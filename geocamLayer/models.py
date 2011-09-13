# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
import datetime, time, random

class BaseFeature(models.Model):
    # demo feature model demonstrating
    # what you need to implement
    def getPosition(self):
        # in Point object
        return Point(0,0)
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
    def __init__(self, position=Point((0,0)), timestamp=time.time(),
                 timespan=datetime.timedelta(), name="Feature",
                 description="Simple feature", properties={}, *args, **kwargs):
        BaseFeature.__init__(self, *args, **kwargs)
        self.position = position
        self.timestamp = timestamp
        self.timespan = timespan
        self.name = name
        self.description = description
        self.properties = properties
        
    def getPosition(self): return self.position
    def getTimeStamp(self): return self.timestamp
    def getTimeSpan(self): return self.timespan
    def getName(self): return self.name
    def getDescriptionHTML(self): return self.description
    def getProperties(self): return self.properties

class RandomFeature(Feature):
    def __init__(self, *args, **kwargs):
        Feature.__init__(self, Point((random.randint(0,180), random.randint(0,180))),
                         time.time(), datetime.timedelta(random.randint(0,3)),
                         "Random Feature", "Random Feature", {}, *args, **kwargs)
