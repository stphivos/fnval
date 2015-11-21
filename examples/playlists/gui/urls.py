from django.conf.urls import url
from gui import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'accounts/login', views.LoginView.as_view(), name='login'),
    url(r'profile', views.ProfileView.as_view(), name='profile'),
    url(r'playlist/(?P<id>\d+)', views.PlaylistView.as_view(), name='playlist_edit'),
    url(r'playlist', views.PlaylistView.as_view(), name='playlist_view'),
]
