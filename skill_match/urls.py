from django.conf.urls import url
from skill_match.views import ListHendersonParks

urlpatterns = (
    url(r'^parks/$', ListHendersonParks.as_view(), name='list_parks'),
)
