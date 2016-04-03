import geocoder
import re
from django.db.models import Count
from django.shortcuts import render
from rest_framework import generics
from skill_match.models import HendersonPark, Match
from django.contrib.gis.db.models.functions import Distance
from skill_match.serializers import HendersonParkSerializer, MatchSerializer
from django.contrib.gis.geos import GEOSGeometry as Geos


###############################################################################
#
# Image URL's used for sport representation
#
###############################################################################

TENNIS_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                 "c_scale,w_200/v1451803727/1451824644_tennis_jegpea.png"
BASKETBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                     "c_scale,w_200/v1451811954/basketball_lxzgmw.png"
FOOTBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                   "c_scale,w_200/v1451812093/American-Football_vbp5ww.png"
SOCCER_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                 "c_scale,w_200/v1451803724/1451824570_soccer_mwvtwy.png"
VOLLEYBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                     "c_scale,w_200/v1451803790/1451824851_" \
                     "volleyball_v2pu0m.png"
PICKLEBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                     "c_scale,w_200/v1451803795/1451824990_" \
                     "table_tennis_uqv436.png"
TROPHY_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                "v1451804013/trophy_200_cnaras.jpg"

###############################################################################
#
# PARK RELATED VIEWS
#
###############################################################################


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
        # Default Point (location) for Henderson, NV
        pnt = Geos('POINT(-114.9817213 36.0395247)', srid=4326)

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

        # Filter by distance to the pnt (location)
        qs = qs.annotate(distance=Distance(
                'location', pnt)).order_by('distance')[:40]

        return qs


class DetailHendersonPark(generics.RetrieveAPIView):
    # Detail View for Park Detail Page.
    queryset = HendersonPark.objects.all()
    serializer_class = HendersonParkSerializer

###############################################################################
#
# MATCH Related Views
#
###############################################################################


class ListCreateMatches(generics.ListCreateAPIView):
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Match.objects.all().order_by('-date')
    serializer_class = MatchSerializer

    def perform_create(self, serializer):

        sport = serializer.initial_data['sport']

        # Choose Image for corresponding sport chosen
        if sport == 'Tennis':
            img_url = TENNIS_IMG_URL
        elif sport == 'Basketball':
            img_url = BASKETBALL_IMG_URL
        elif sport == 'Football':
            img_url = FOOTBALL_IMG_URL
        elif sport == 'Soccer':
            img_url = SOCCER_IMG_URL
        elif sport == 'Volleyball':
            img_url = VOLLEYBALL_IMG_URL
        elif sport == 'Pickleball':
            img_url = PICKLEBALL_IMG_URL
        else:
            img_url = TROPHY_IMG_URL

        # Assign logged in user to Math's Creator (in serializer.save)
        user = self.request.user

        serializer.save(creator=user, img_url=img_url)

        # OLD CODE TO ADD COURTS TO PARKS WHERE THEY DIDN'T ALREADY EXIST
        #
        # match = serializer.save(creator=user, img_url=img_url)
        # Create new Court for the park selected if it doesn't exist already.
        # already_exists = Court.objects.filter(park=match.park,
        #                                       sport=match.sport)
        # if not already_exists:
        #     Court.objects.create(park=match.park, sport=match.sport)
        # create_match_notify(match)

    def get_queryset(self):
        """
        /matches?sport=tennis
        /matches?username=tennismonster
        /matches?lat=42.3601&lng=71.0589
        /matches?zip=89074

        Querysets:
        1. home: filter for only OPEN matches ordered by date of match upcoming
        2. lat and long (latitude and longitude): use to order by distance
        3. *zip code: use to order by distance
        4. sport: only include parks with that sport
        5. username: filter by only matches the user with that username
           participated in

        * Uses Nominatim from the geopy library to get latitude and longitude
        based on the zipcode.

        Default Ordering: by distance
        If no location provided, default location is Las Vegas, NV.
        Uses Geos Point objects to order by distance.

        :return: Matches ordered by distance
        """
        qs = super().get_queryset()
        sport = self.request.query_params.get('sport', None)
        username = self.request.query_params.get('username', None)
        latitude = self.request.query_params.get('lat', None)
        longitude = self.request.query_params.get('long', None)
        zip_code = self.request.query_params.get('zip', None)

        # Filter by specific sport
        if sport:
            sport = sport.title()
            qs = qs.filter(sport=sport).filter(status='Open')

        # Filter for only matches involving a certain user
        if username:
            qs = Match.objects.filter(players__username=username).\
                order_by('-date')

        # Filter by distance of latitude and longitude, zip_code, or default
        if latitude and longitude:
            pnt = Geos('POINT(' + str(longitude) + ' ' + str(latitude) + ')',
                       srid=4326)
            qs = qs.filter(status='Open')
        elif zip_code:
            # Geocode to get latitude and longitude from zip_code
            g = geocoder.google(zip_code + ' NV')
            g_latitude = g.latlng[0]
            g_longitude = g.latlng[1]
            pnt = Geos('POINT(' + str(g_longitude) + ' ' +
                       str(g_latitude) + ')', srid=4326)
            qs = qs.filter(status='Open')
        else:
            # Default Point (location) for Henderson, NV
            pnt = Geos('POINT(-114.9817213 36.0395247)', srid=4326)

        qs = qs.annotate(distance=Distance(
                'park__location', pnt)).order_by('distance')[:40]

        return qs
