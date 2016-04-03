from rest_framework import serializers
from skill_match.models import HendersonPark, Amenity, Court, Match


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


class HendersonParkSerializer(serializers.ModelSerializer):
    court_set = CourtSerializer(many=True, read_only=True)
    amenities = serializers.SerializerMethodField()
    distance = serializers.DecimalField(source='distance.mi', max_digits=10,
                                        decimal_places=2, required=False,
                                        read_only=True)

    def get_amenities(self, obj):
        amenities = obj.amenity_set.all()
        return [amenity.name for amenity in amenities]

    class Meta:
        model = HendersonPark
        fields = ('id', 'name', 'address', 'url', 'img_url', 'court_set',
                  'amenities', 'distance')
        read_only_fields = ('name', 'address', 'url', 'img_url')


# class MatchSerializer(serializers.ModelSerializer):
#     park_name = serializers.ReadOnlyField(source='park.name')
#     creator_name = serializers.ReadOnlyField(source='creator.username')
#     time = serializers.TimeField(format="%I:%M %p")
#     players = SimpleUserSerializer(many=True, read_only=True)
#     date = serializers.DateField(format="%A %b, %d")
#     distance = serializers.DecimalField(source='distance.mi', max_digits=10,
#                                         decimal_places=2, required=False,
#                                         read_only=True)
#
#     class Meta:
#         model = Match
#         fields = ('id', 'creator', 'creator_name', 'description', 'park',
#                   'park_name', 'sport', 'other', 'skill_level', 'date', 'time',
#                   'players', 'img_url', 'is_open', 'is_completed',
#                   'is_confirmed', 'is_challenge', 'challenge_declined',
#                   'distance')
#
#         read_only_fields = ('id', 'creator', 'players', 'is_open',
#                             'is_completed', 'is_confirmed', 'img_url',
#                             'is_challenge', 'challenge_declined', 'distance')
#
#     def create(self, validated_data):
#         """
#         Creating User is passed and added to the players(ManyToMany) on Match
#         :param validated_data:
#         :return:
#         """
#         challenged = validated_data.get('challenged', None)
#         if challenged:
#             challenged = validated_data.pop('challenged')
#         match = super().create(validated_data)
#         creator = validated_data['creator']
#         match.players.add(creator)
#         if match.is_challenge:
#             match.players.add(challenged)
#         match.save()
#         return match


class MatchSerializer(serializers.ModelSerializer):
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

    read_only_fields = ('id', 'creator', 'players', 'status', 'img_url',
                        'distance')

    class Meta:
        model = Match
        fields = ('id', 'creator', 'creator_name', 'description', 'park',
                  'park_name', 'sport', 'other', 'skill_level', 'date',
                  'time', 'status', 'distance')
