from django.conf.urls import url
from gui import views

urlpatterns = [
    url(r'^$', views.Home.as_view(), name='home'),
    url(r'accounts/login', views.Login.as_view(), name='login'),
    url(r'profile', views.Profile.as_view(), name='profile'),
    url(r'playlist/(?P<id>\d+)', views.Playlist.as_view(), name='playlist_edit'),
    url(r'playlist', views.Playlist.as_view(), name='playlist_view'),
]
