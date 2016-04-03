from django.conf.urls import url
from skill_match.views import ListHendersonParks, DetailHendersonPark, \
    ListCreateMatches

urlpatterns = (
    url(r'^parks/$', ListHendersonParks.as_view(), name='list_parks'),
    url(r'^parks/(?P<pk>\d+)/$', DetailHendersonPark.as_view(),
        name='detail_park'),
    url(r'^matches/$', ListCreateMatches.as_view(), name='list_matches'),
)
