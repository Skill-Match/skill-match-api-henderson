import geocoder
import re
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render
from rest_framework import generics
from skill_match.exceptions import NotInMatch, NonExistingPlayer, \
    OneFeedbackAllowed, NoPlayerToConfirmOrDecline, \
    OnlyCreatorMayConfirmOrDecline, AlreadyConfirmed, SelfSignUp, AlreadyJoined
from skill_match.models import HendersonPark, Match, Feedback
from django.contrib.gis.db.models.functions import Distance
from skill_match.serializers import HendersonParkSerializer, MatchSerializer, \
    FeedbackSerializer, ChallengerMatchSerializer
from django.contrib.gis.geos import GEOSGeometry as Geos
from skill_match.tasks import update_skills, test_task


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

        # Assign logged in user to Math's Creator (in serializer.save)
        user = self.request.user

        challenged_player = serializer.initial_data.get('challenged', None)
        if challenged_player:
            challenged = User.objects.get(pk=challenged_player)
            serializer.save(creator=user, players=[user, challenged],
                            status='Challenge')
        else:
            # Set creator as requesting user, add img_url,
            serializer.save(creator=user, players=[user, ])

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


class DetailUpdateMatch(generics.RetrieveUpdateDestroyAPIView):
    # Detail Update Match
    # permission_classes = (IsOwnerOrReadOnly,)
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

    def perform_update(self, serializer):

        previous = self.get_object()
        new_sport = serializer.validated_data['sport']

        if previous.sport == new_sport:
            serializer.save()
        else:
            if new_sport == 'Tennis':
                img_url = TENNIS_IMG_URL
            elif new_sport == 'Basketball':
                img_url = BASKETBALL_IMG_URL
            elif new_sport == 'Football':
                img_url = FOOTBALL_IMG_URL
            elif new_sport == 'Soccer':
                img_url = SOCCER_IMG_URL
            elif new_sport == 'Volleyball':
                img_url = VOLLEYBALL_IMG_URL
            elif new_sport == 'Pickleball':
                img_url = PICKLEBALL_IMG_URL
            else:
                img_url = TROPHY_IMG_URL

            serializer.save(img_url=img_url)


###############################################################################
#
# JOIN, LEAVE, DECLINE, CONFIRM MATCH
#
###############################################################################


class JoinMatch(generics.UpdateAPIView):
    # permission_classes = (permissions.IsAuthenticated,)
    queryset = Match.objects.all()
    serializer_class = ChallengerMatchSerializer

    def perform_update(self, serializer):
        """
        Gets all players from serializer and puts them in player_list. Add the
        User making the request to the player_list.
        If Sport is Tennis, close match and notify match creator using
        join_match_notify() from notifications.
        :param serializer:
        :return:
        """
        # Get joiner as requesting user
        joiner = self.request.user
        # Get creator as the matches creator
        creator = serializer.instance.creator

        # ?????????????????????
        #
        # Disallow creator to join own match, really need this?
        if joiner == creator:
            raise SelfSignUp

        # Get list of players in match
        players = serializer.instance.players.all()
        player_list = list(players)

        # Don't allow multiple join by same user.
        if joiner in player_list:
            raise AlreadyJoined

        # Add player to list in matches
        player_list.append(joiner)

        # Update status if Tennis or Pickleball, save serializer with new
        # player list.
        sport = serializer.instance.sport
        if sport == 'Tennis':
            serializer.save(players=player_list, status='Joined')
            # match = serializer.save(players=player_list, is_open=True)
            # join_match_notify(match, joiner)
        else:
            serializer.save(players=player_list)


class LeaveMatch(generics.UpdateAPIView):
    # permission_classes = (permissions.IsAuthenticated,)
    queryset = Match.objects.all()
    serializer_class = ChallengerMatchSerializer

    def perform_update(self, serializer):
        """
        Users may leave a match if they get tired waiting for Match creator to
        confirm.
        If requesting user is in match, and the match is not confirmed already,
        they are removed from player_list.
        If sport is Tennis, match opens up again.
        Match creator is notified that the user left match and match is
        open again.
        :param serializer:
        :return:
        """

        # ???
        #
        # Raise error if Match is already confirmed. Say you must cancel
        # instead.
        if serializer.instance.status == 'Confirmed':
            raise AlreadyConfirmed

        # ?? Raise error if user is the creator. Do I need this? Prob not.
        leaver = self.request.user
        if leaver == serializer.instance.creator:
            raise SelfSignUp

        # Get sport and player_list
        sport = serializer.instance.sport
        players = serializer.instance.players.all()
        player_list = list(players)

        # ?? Raise error if leaver not in the match. Do I need this?
        if leaver not in player_list:
            raise NotInMatch

        # Remove player from Match
        player_list.remove(leaver)

        # If sport is Tennis or 1v1, status = Open
        if sport == 'Tennis':
            serializer.save(players=player_list, status='Open')
            # match = serializer.save(players=player_list, status='Open')
            # leave_match_notify(match, leaver)
        else:
            serializer.save(players=player_list)


class DeclineMatch(generics.UpdateAPIView):
    # Add permission as match owner?
    # permission_classes = (permissions.IsAuthenticated,)
    queryset = Match.objects.all()
    serializer_class = ChallengerMatchSerializer

    def perform_update(self, serializer):
        """
        Remove User (challenger) from Match. Notify match challenger.
        Match is opened again if not a challenge.

        :param serializer:
        :return:
        """
        # ?? Raise error to decline match that has no player
        if serializer.instance.players.count() == 1:
            raise NoPlayerToConfirmOrDecline

        # Decliner is requesting user
        decliner = self.request.user

        # ?? Raise error if decliner is not the creator of the match , need this?
        if not decliner == serializer.instance.creator:
                raise OnlyCreatorMayConfirmOrDecline

        serializer.save(players=[decliner, ], status='Open')

        # Get Challenger as the other player in a 1v1 match
        # challenger = serializer.instance.players.exclude(id=decliner.id)[0]

        # Remove player from match and re-open the match
        # decline_match_notify(match, challenger)

        # # CHALLENGE CODE NEEDS REFACTOR
        # if serializer.instance.status == 'Challenge':
        #     if challenger == serializer.instance.creator:
        #         match = serializer.save(challenge_declined=True)
        #         # [TEMP REMOVE] challenge_declined_notify(match, challenger)
        # else:



class ConfirmMatch(generics.UpdateAPIView):
    # Add permission as match owner?
    # permission_classes = (permissions.IsAuthenticated, )
    queryset = Match.objects.all()
    serializer_class = ChallengerMatchSerializer

    def perform_update(self, serializer):
        """
        Confirm match. Only change here is is_confirmed=True. Needs refactor
        with Match model
        :param serializer:
        :return:
        """
        # ?? Raise error to decline match that has no player
        if serializer.instance.players.count() == 1:
            raise NoPlayerToConfirmOrDecline

        # Get confirmer as requesting User
        confirmer = self.request.user

        if not confirmer == serializer.instance.creator:
                raise OnlyCreatorMayConfirmOrDecline

        serializer.save(status='Confirmed')

        # Old code for Challenge Match needs refactoring
        #
        # if serializer.instance.is_challenge:
        #     match = serializer.save(is_confirmed=True)
        #     # [TEMP REMOVE] challenge_accepted_notify(match)
        # else:
        #     if not confirmer == serializer.instance.creator:
        #         raise OnlyCreatorMayConfirmOrDecline
        #
        #     match = serializer.save(is_confirmed=True)
        #     confirm_match_notify(match)


###############################################################################
#
# FEEDBACK Related Views
#
###############################################################################


class CreateFeedback(generics.CreateAPIView):
    # permission_classes = (permissions.IsAuthenticated,)
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def perform_create(self, serializer):
        """If no player, Get match_id from serializer. Find Match object with
           match_id. Use Match object to find player and reviewer from the
           match. (Reviewer = logged in user.
          If player, use player_id to find User to be reviewed
          Error if they already provided Feedback for that player.
        """
        # Reviewer is the user making request
        reviewer = self.request.user

        # Look up Match related to feedback
        match_id = serializer.initial_data['match']
        match = Match.objects.get(pk=match_id)

        # Assure user is in the related match.
        if reviewer not in match.players.all():
            raise NotInMatch

        # ---RATE BY USER ID--- # Check to see if "player: id" was in request
        player_id = serializer.initial_data.get('player', None)
        if player_id:

            # if id for player does not match a user , error
            existing_user = User.objects.filter(id=player_id)
            if not existing_user:
                raise NonExistingPlayer

            # Get User for player identified
            player = User.objects.get(pk=player_id)

            # ONLY ONE FEEDBACK ALLOWED
            existing_feedback = match.feedback_set.filter(reviewer=reviewer,
                                                          player=player)
            if existing_feedback:
                raise OneFeedbackAllowed
            feedback = serializer.save(player=player, reviewer=reviewer)

        # RATE WITHOUT PLAYER ID (1v1) ONLY!
        else:
            # ONLY ONE FEEDBACK ALLOWED
            existing_feedback = match.feedback_set.filter(reviewer=reviewer)
            if existing_feedback:
                raise OneFeedbackAllowed

            # Get the player in the match who is not the reviewer
            player = match.players.exclude(id=reviewer.id)[0]

            feedback = serializer.save(player=player, reviewer=reviewer)

            # Update feedback asynchronously
            test_task.delay()
            update_skills.delay(feedback.player.id, feedback.match.sport)
