from django.conf.urls import url
from skill_match.views import ListHendersonParks, DetailHendersonPark, \
    ListCreateMatches, DetailUpdateMatch, JoinMatch, LeaveMatch, DeclineMatch, \
    ConfirmMatch, CreateFeedback

urlpatterns = (
    url(r'^parks/$', ListHendersonParks.as_view(), name='list_parks'),
    url(r'^parks/(?P<pk>\d+)/$', DetailHendersonPark.as_view(),
        name='hendersonpark-detail'),
    url(r'^matches/$', ListCreateMatches.as_view(), name='list_matches'),
    url(r'^matches/(?P<pk>\d+)/$', DetailUpdateMatch.as_view(),
        name='match-detail'),
    url(r'^matches/(?P<pk>\d+)/join$', JoinMatch.as_view(),
        name='join_match'),
    url(r'^matches/(?P<pk>\d+)/leave$', LeaveMatch.as_view(),
        name='leave_match'),
    url(r'^matches/(?P<pk>\d+)/decline$', DeclineMatch.as_view(),
        name='decline_match'),
    url(r'^matches/(?P<pk>\d+)/confirm$', ConfirmMatch.as_view(),
        name='confirm_match'),
    url(r'^feedbacks/$, CreateFeedback.as_view()', name='create_feedback')
)
