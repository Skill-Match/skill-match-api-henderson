from django.conf.urls import url
from users.views import ListUsers, RegisterUser, DetailUpdateUser, \
    ObtainAuthToken

urlpatterns = (
    url(r'^$', ListUsers.as_view(), name='list_users'),
    url(r'^register/$', RegisterUser.as_view(), name='register_user'),
    url(r'^(?P<pk>\d+)/$', DetailUpdateUser.as_view(),
        name='detail_update_user'),
    url(r'^get-token/$', ObtainAuthToken.as_view(),
        name='obtain_auth_token'),

)
