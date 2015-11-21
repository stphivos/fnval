import json
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, QueryDict
from django.utils.decorators import method_decorator
from django.views.generic import View
from gui.models import Playlist


class AuthenticationMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AuthenticationMixin, self).dispatch(request, *args, **kwargs)


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Welcome to playlists!')


class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'login.html')

    def post(self, request, *args, **kwargs):
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return redirect('/')
            else:
                return HttpResponse('Unauthorized', status=401)
        else:
            raise Http404


class ProfileView(AuthenticationMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('User profile')


class PlaylistView(AuthenticationMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('User playlist')

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        p = Playlist(
            name=data['name'],
            user=request.user
        )
        p.save()
        return HttpResponse('Playlist created')

    def put(self, request, *args, **kwargs):
        # skipping the following check will allow any authenticated user to edit other users' playlists
        # if int(kwargs['id']) not in [x.id for x in request.user.playlist_set.all()]:
        #     return HttpResponse('Users can only modify their own playlists.', status=403)
        p = Playlist.objects.get(pk=kwargs['id'])
        data = QueryDict(request.body)
        p.name = data['name']
        p.save()
        return HttpResponse('Playlist updated')

    def delete(self, request, *args, **kwargs):
        if int(kwargs['id']) not in [x.id for x in request.user.playlist_set.all()]:
            return HttpResponse('Users can only delete their own playlists.', status=403)
        return HttpResponse('Playlist deleted')
