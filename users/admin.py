from django.contrib import admin
from users.models import Profile


@admin.register(Profile)
class HendersonParkAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'age', 'wants_texts', 'phone_number')