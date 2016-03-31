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
        fields = ('id', 'name', 'parks')


class CourtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = ('id', 'park', 'sport', 'other', 'img_url')


class HendersonParkSerializer(serializers.ModelSerializer):
    class Meta:
        model = HendersonPark
        fields = ('name', 'address', 'url', 'img_url')
        read_only_fields = ('name', 'address', 'url', 'img_url')
