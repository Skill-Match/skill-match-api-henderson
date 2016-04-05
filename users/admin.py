from django.contrib import admin
from users.models import Profile, Skill


@admin.register(Profile)
class HendersonParkAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'age', 'wants_texts', 'phone_number')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('player', 'sport', 'skill', 'sportsmanship', 'punctuality',
                    'num_feedbacks')
