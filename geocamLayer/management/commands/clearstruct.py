#!/usr/bin/env python
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os, os.path, shutil

class Command(BaseCommand):
    args = ""
    help = "This command deletes an existing file structure for points"

    root = os.path.join(settings.MEDIA_ROOT, "tiles")

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing files...\n")
        if os.path.exists(self.root):
            shutil.rmtree(self.root)
        self.stdout.write("Done.\n")
