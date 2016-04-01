import geocoder
import re
from django.db.models import Count
from django.shortcuts import render
from rest_framework import generics
from skill_match.models import HendersonPark
from django.contrib.gis.db.models.functions import Distance
from skill_match.serializers import HendersonParkSerializer
from django.contrib.gis.geos import GEOSGeometry as Geos


class ListHendersonParks(generics.ListAPIView):
    queryset = HendersonPark.objects.all()
    serializer_class = HendersonParkSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        latitude = self.request.query_params.get('lat', None)
        longitude = self.request.query_params.get('lng', None)
        search = self.request.query_params.get('search', None)
        sport = self.request.query_params.get('sport', None)
        courts = self.request.query_params.get('courts', None)
        pnt = None

        # Filter by specific sport
        if sport:
            sport = sport.title()
            qs = qs.filter(court__sport=sport)

        # Filter: only Parks with Courts
        if courts:
            qs = qs.annotate(count=Count('court')).exclude(count=0)

        # Filter by location if search is a zip_code (5 digit number)
        # Otherwise use search to find HendersonParks with a name
        # containing the search term
        if search:
            zip_code = re.match('^\d{5}$', search)
            if zip_code:
                g = geocoder.google(search + ' NV')
                g_latitude = g.latlng[0]
                g_longitude = g.latlng[1]
                pnt = Geos('POINT(' + str(g_longitude) + ' ' +
                           str(g_latitude) + ')', srid=4326)
            else:
                qs = qs.filter(name__icontains=search)

        # If lat and lng are passed set location to filter by
        if latitude and longitude:
            pnt = Geos('POINT(' + str(longitude) + ' ' + str(latitude) + ')',
                       srid=4326)

        # If no location provided by search (zip_code) or lat & lng, set
        # default location to Henderson, NV
        if not pnt:
            pnt = Geos('POINT(-114.9817213 36.0395247)', srid=4326)

        # Filter by distance to the pnt (location)
        qs = qs.annotate(distance=Distance(
                'location', pnt)).order_by('distance')[:20]

        return qs
