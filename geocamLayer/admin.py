# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.contrib import admin

from geocamLayer.models import Feature, QuadTreeCell

class FeatureAdmin(admin.ModelAdmin):
    list_display = ('lat',
                    'lng',
                    'name',
                    'description',
                    'cell')

class QuadTreeCellAdmin(admin.ModelAdmin):
    list_display = ('zoom',
                    'x',
                    'y',
                    'count',
                    'isLeaf',
                    'lng',
                    'lat')

admin.site.register(Feature, FeatureAdmin)
admin.site.register(QuadTreeCell, QuadTreeCellAdmin)
