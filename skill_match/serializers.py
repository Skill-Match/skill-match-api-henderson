from rest_framework import serializers
from skill_match.models import HendersonPark, Amenity, Court

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
