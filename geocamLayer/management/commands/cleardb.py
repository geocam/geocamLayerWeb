#!/usr/bin/env python
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from geocamLayer import models
import sys

class Command(BaseCommand):
    args = ""
    help = "This command clears the database of existing points"

    @transaction.commit_manually
    def handle(self, *args, **options):
        self.stdout.write("Getting all objects...\n")
        features = list(models.Feature.objects.all())
        self.stdout.write("%s objects in total\n" % len(features))
        numpoints = len(features)
        self.stdout.write("Deleting all objects...\n")
        for i,point in enumerate(features):
            self.stdout.write('\r')
            self.stdout.write(str(int((float(i)/numpoints)*100)))
            self.stdout.write('%')
            self.stdout.flush()
            point.delete()
        self.stdout.write('\nCommitting...\n')
        transaction.commit()
        self.stdout.write('Done.\n')
            
