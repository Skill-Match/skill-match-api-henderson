from rest_framework import serializers
from skill_match.models import HendersonPark, Amenity, Court, Match, Feedback


###############################################################################
#
# PARK AND COURT RELATED SERIALIZERS
#
###############################################################################


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ('name',)


class CourtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = ('sport', 'other', 'img_url')


class HendersonParkSerializer(serializers.HyperlinkedModelSerializer):
    court_images = serializers.SerializerMethodField()
    amenities = serializers.SerializerMethodField()
    distance = serializers.DecimalField(source='distance.mi', max_digits=10,
                                        decimal_places=2, required=False,
                                        read_only=True)

    def get_court_images(self, obj):
        courts = obj.court_set.all()
        return [court.img_url for court in courts]

    def get_amenities(self, obj):
        amenities = obj.amenity_set.all()
        return [amenity.name for amenity in amenities]

    class Meta:
        model = HendersonPark
        fields = ('url', 'id', 'name', 'address', 'img_url', 'distance',
                  'amenities', 'henderson_url', 'court_images')
        read_only_fields = ('name', 'address', 'img_url', 'henderson_url')


class MatchSerializer(serializers.HyperlinkedModelSerializer):
    park_name = serializers.ReadOnlyField(source='park.name')
    creator_name = serializers.ReadOnlyField(source='creator.username')
    time = serializers.TimeField(format="%I:%M %p")
    # add players
    date = serializers.DateField(format="%A %b, %d")
    distance = serializers.DecimalField(source='distance.mi',
                                        max_digits=10,
                                        decimal_places=2,
                                        required=False,
                                        read_only=True)

    class Meta:
        model = Match
        fields = ('url', 'id', 'creator', 'creator_name', 'title',
                  'description', 'park',
                  'park_name', 'sport', 'other', 'img_url', 'skill_level',
                  'date', 'time', 'players', 'status', 'distance')
        read_only_fields = ('url', 'id', 'creator', 'players', 'status',
                            'img_url', 'distance')


# Simple Serializer for Match Joins, Leaves, Declines, Confirms, Cancels
class ChallengerMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ('id', 'creator', 'description', 'park', 'sport',
                  'skill_level', 'date', 'time', 'players',
                  'status')
        read_only_fields = ('id', 'creator', 'description', 'park', 'sport',
                            'skill_level', 'date', 'time', 'players',
                            'status')


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('id', 'reviewer', 'player', 'match', 'skill',
                  'sportsmanship', 'punctuality',)
        read_only_fields = ('id', 'reviewer', 'player',)
