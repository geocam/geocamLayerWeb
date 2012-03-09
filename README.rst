1st paragraph describes point
2nd paragraph "here is the exact install instructions"

Documentation for the use of this clustering software

The whole point of this clustering software is to be completely expandable without the need for modification of the code. The code as-is only needs to be provided with a list of objects that have the same functions as the ones in the models.py BaseFeature class. All of the clustering takes place within the "get" function, there is no database interaction whatsoever. This is in contrast to the Django system that this is based on, where most of the interactions are with databases.

The "get" function takes the request as a first argument and the list of points as the second. It has two encoding options, geojson and kml.

The geojson is formatted as follows::

  {
    "type": "FeatureCollection",
    "features":
    [
      {"geometry": {
        "type":"Point",
        "coordinates":[
          [
            (lat-coordinate of feature),
  	  (lng-coordinate of feature)
  	]
        ]
      },
      "properties": {
        (for clusters)
        "bbox": [
          (north coordinate of bounding box containing points in cluster),
  	(east coordinate),
  	(south coordinate),
  	(west coordinate)
        ],
        (for clusters:)
        "numpoints":(number of points in cluster),
        "subtype":"cluster"
        (for other points:)
        "timestamp":(timestamp of point),
        "timespan":(timespan of point),
        "name":(name of point),
        "description":(description of point),
        (all other properties that are provided by the getProperties function)
      }
      },
      (all the other points on the map)
      ]
  }
  
The KML is formatted as follows:

TODO: this section.

A sample server-side implementation of this could be::

  url_patterns += [
      (r'^points/', 'views.get', {'objects':objects})
  ]

The values passed to this "get" views are passed in the URL ("GET" parameters) and are as follows (all are optional):

cluster: 1 or 0 for yes or no, respectively
bbox: toUrlValue() of a LatLngBounds gmap2 object
encoding: geojson or kml
start: start index
end: end index
reverse: 1 or 0 for yes or no, respectively

A sample URL could be::

  http://www.server.com/point/?cluster=1&bbox=7.095248,-142.99263,46.496068,-101.13472

The client side interface for the geojson is designed to be easy to read for gmap clients. The way that it is designed to be implemented is json parsing through an XMLHTTPRequest, which then pushes points or clusters depending on the subtype to the gmap interface. An example implementation is provided in the static folder.

The positions and bounding boxes of the objects sent through the geojson are intended to work well with google maps, and are in the right order to enable direct loading of the points into the gmap. The bounds included in each cluster can be translated into LatLngBounds with no change in order, which can then be passed to the fitBounds method which will correctly zoom down to a point where you can see all the points in the cluster.

To get the included demo running:

1. Install django
2. cd into example
3. python manage.py syncdb
4. python manage.py runserver
5. demo is now running on localhost:8000

.. o  __BEGIN_LICENSE__
.. o  Copyright (C) 2008-2010 United States Government as represented by
.. o  the Administrator of the National Aeronautics and Space Administration.
.. o  All Rights Reserved.
.. o  __END_LICENSE__
