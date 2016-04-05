from django.contrib import admin
from skill_match.models import HendersonPark, Amenity, Court, Match, Feedback


@admin.register(HendersonPark)
class HendersonParkAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'henderson_url', 'img_url', 'location')


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('id', 'park', 'sport', 'other', 'img_url')


@admin.register(Match)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'description', 'sport', 'other',
                    'skill_level', 'status', 'date', 'img_url', )


@admin.register(Feedback)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('id', 'reviewer', 'player', 'match', 'skill',
                    'sportsmanship', 'punctuality')
