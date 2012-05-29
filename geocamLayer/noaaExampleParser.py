# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from geocamLayer.models import Feature
import random


def parseDegrees(data, positiveDirection):
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


def parseLatitude(latStr):
    return parseDegrees(latStr, 'N')


def parseLongitude(latStr):
    return parseDegrees(latStr, 'E')


def readNoaaWeatherStations(fname):
    for line in open(fname):
        data = line.strip().split(';')

        blockNumber, stationNumber, icaoLocation, placeName,\
            state, countryName, wmoRegion, stationLatitude,\
            stationLongitude, upperAirLatitude, upperAirLongitude,\
            stationElevation, upperAirElevation, rbsnIndicator\
            = data

        yield Feature(lat=parseLatitude(stationLatitude),
                      lng=parseLongitude(stationLongitude),
                      name=placeName,
                      description=countryName,
                      pkey=random.random())
