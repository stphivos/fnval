from django.http import JsonResponse, HttpResponse


class ExceptionMiddleware(object):
    def process_exception(self, request, exception):
        return HttpResponse('{0}: {1}'.format(type(exception).__name__, exception.message), status=500)
