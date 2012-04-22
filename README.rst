
GeocamLayer is a library for web mapping that enables efficient browsing
of massive sets of map placemarks.

Its Python/Django server component provides a map feed which answers
location-specific queries. When the query covers a wide map area, it
performs server-side clustering of placemarks to keep the response size
bounded regardless of the overall size of the data set.

Its JavaScript client component, built on the Google Maps API,
automatically performs the queries needed to populate the map with
placemarks and clusters based on the map viewport.

Dependencies:

 * Python_
 * Django_
 * Git_ (used to download this module; or just `grab a tarball`_)

.. _python: http://python.org/download/
.. _django: https://docs.djangoproject.com/en/dev/intro/install/
.. _git: http://git-scm.com/download
.. _grab a tarball: https://github.com/geocam/geocamLayerWeb/downloads

Installation::

  git clone http://github.com/geocam/geocamLayerWeb
  cd geocamLayerWeb/example
  ./manage.py syncdb
  ./manage.py runserver

The server should now be running on localhost:8000. The web page should be a full-page Google map, which should automatically load points and clusters as you move the map around. Clicking on a cluster should bring you down to a zoom level that includes all the points in the cluster.

Technical Details
-----------------

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
      (r'^points/(?P<zoom>[-.0-9]*)/(?P<x>[-.0-9]*)/(?P<y>[-.0-9]*)', 'views.points', {'objects':objects})
  ]

The values passed to this "get" views are passed in the URL ("GET" parameters) and are as follows (all are optional):

cluster: 1 or 0 for yes or no, respectively
bbox: toUrlValue() of a LatLngBounds gmap2 object
encoding: geojson or kml
start: start index
end: end index
reverse: 1 or 0 for yes or no, respectively

A sample URL could be::

  http://www.server.com/points/5.997071742313324/-75.00732421875/27.350839455709888?cluster=1

The client side interface for the geojson is designed to be easy to read for gmap clients. The way that it is designed to be implemented is json parsing through an XMLHTTPRequest, which then pushes points or clusters depending on the subtype to the gmap interface. An example implementation is provided in the static folder.

The positions and bounding boxes of the objects sent through the geojson are intended to work well with google maps, and are in the right order to enable direct loading of the points into the gmap. The bounds included in each cluster can be translated into LatLngBounds with no change in order, which can then be passed to the fitBounds method which will correctly zoom down to a point where you can see all the points in the cluster.

.. o  __BEGIN_LICENSE__
.. o  Copyright (C) 2008-2010 United States Government as represented by
.. o  the Administrator of the National Aeronautics and Space Administration.
.. o  All Rights Reserved.
.. o  __END_LICENSE__
