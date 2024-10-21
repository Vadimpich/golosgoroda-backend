from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin

from api.views import session_storage

User = get_user_model()


class SessionMiddleware(MiddlewareMixin):
    def process_request(self, request):

        session_id = request.COOKIES.get("session_id")

        if session_id:
            username = session_storage.get(session_id).decode('utf-8')
            if username:
                request.user = User.objects.get(username=username)
            else:
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
