from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.views.generic import View


class AuthenticationMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AuthenticationMixin, self).dispatch(request, *args, **kwargs)


class Home(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Welcome to playlists!')


class Login(View):
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


class Profile(AuthenticationMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('User profile')


class Playlist(AuthenticationMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('User playlist')

    def post(self, request, *args, **kwargs):
        return HttpResponse('Playlist created')

    def put(self, request, *args, **kwargs):
        # skipping the following check will allow any authenticated user to edit other users' playlists
        # if int(kwargs['id']) not in [x.id for x in request.user.playlist_set.all()]:
        #     return HttpResponse('Users can only modify their own playlists.', status=403)
        return HttpResponse('Playlist updated')

    def delete(self, request, *args, **kwargs):
        if int(kwargs['id']) not in [x.id for x in request.user.playlist_set.all()]:
            return HttpResponse('Users can only delete their own playlists.', status=403)
        return HttpResponse('Playlist deleted')
