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
    def __init__(self, lng, lat, timestamp=time.time(),
                 timespan=datetime.timedelta(), name="Feature",
                 description="Simple feature", *args, **kwargs):# properties={}, *args, **kwargs):
        BaseFeature.__init__(self, *args, **kwargs)
        self.lng, self.lat = lng,lat
        self.timestamp = timestamp
        self.timespan = timespan
        self.name = name
        self.description = description
        #self.properties = properties
        
    def getPosition(self): return (self.lng,self.lat)
    def getTimeStamp(self): return self.timestamp
    def getTimeSpan(self): return self.timespan
    def getName(self): return self.name
    def getDescriptionHTML(self): return self.description
    def getProperties(self): return {} # self.properties

class RandomFeature(Feature):
    def __init__(self, *args, **kwargs):
        Feature.__init__(self, random.randint(-180,180), random.randint(-90,90),
                         time.time(), datetime.timedelta(random.randint(0,3)),
                         "Random Feature", "Random Feature", *args, **kwargs)# {}, *args, **kwargs)
