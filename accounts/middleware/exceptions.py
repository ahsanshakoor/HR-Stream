from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

from accounts.exceptions.custom import ObjectNotFound


class ExceptionMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        if type(exception) == ObjectNotFound:
            return render(request, exception.template)
        return None