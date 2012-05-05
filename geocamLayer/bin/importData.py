#!/usr/bin/env python
# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import sys
import itertools

from django.db import transaction

from geocamLayer.noaaExampleParser import readNoaaWeatherStations
from geocamLayer.quadTree import QuadTree
from geocamLayer.models import Feature, QuadTreeCell


def importFeatures(tree, features, maxNumFeatures):
    if maxNumFeatures:
        features = itertools.islice(features, maxNumFeatures)
    for feature in features:
        tree.addFeature(feature)
        sys.stdout.write('.')
        sys.stdout.flush()


@transaction.commit_manually
def cleanData():
    print 'deleting old data'
    # for loops are a work around for bulk delete problem in sqlite
    # with objects.all().delete()
    for f in Feature.objects.all():
        f.delete()
    for q in QuadTreeCell.objects.all():
        q.delete()
    transaction.commit()


def importData(opts):
    if opts.clean:
        cleanData()

    tree = QuadTree()
    if opts.noaa:
        sys.stdout.write('noaa import')
        importFeatures(tree, readNoaaWeatherStations(opts.noaa), opts.maxNumFeatures)
    tree.finish()
    print
    print
    tree.debugStats()


def main():
    import optparse
    parser = optparse.OptionParser('usage: %prog')
    parser.add_option('-n', '--maxNumFeatures',
                      type='int',
                      help='Cap on number of features to import')
    parser.add_option('-c', '--clean',
                      action='store_true', default=False,
                      help='[USE CAUTION!] Delete old data before import')
    parser.add_option('--noaa',
                      help='Path to NOAA weather stations example file')
    opts, args = parser.parse_args()
    if args:
        parser.error('expected no arguments')
    importData(opts)


if __name__ == '__main__':
    main()
