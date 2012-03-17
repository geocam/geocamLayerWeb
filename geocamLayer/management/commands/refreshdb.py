#!/usr/bin/env python
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from optparse import make_option
from geocamLayer.models import *
import sys

class Command(BaseCommand):
    args = "<num_points>"
    help = "This command refreshed the point database"

    option_list = BaseCommand.option_list + (
        make_option('--clear',
                    action="store_true",
                    dest="clear_db",
                    default=False,
                    help="Clear database before adding new objects"
                    ),
        )

    def handle(self, *args, **options):
        stdout = sys.stdout
        sys.stdout = self.stdout
        transaction.commit_manually()
        if not args:
            print "No args found, using 1000 points"
            numpoints = 1000
        else:
            try: numpoints = int(args[0])
            except ValueError: raise CommandError("Invalid first argument")
        if options['clear_db']:
            print "Clearing database..."
            Feature.objects.all().delete()
        print "Generating %s points..." % numpoints
        for i in xrange(numpoints):
            sys.stdout.write('\r')
            sys.stdout.write(str(int((float(i)/numpoints)*100)))
            sys.stdout.write('%')
            sys.stdout.flush()
            feature = Feature.randomFeature()
            feature.save()
        print
        transaction.commit()
        sys.stdout = stdout
