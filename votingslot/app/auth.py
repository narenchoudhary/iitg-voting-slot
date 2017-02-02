import poplib

from .models import User


class WebMailAuthenticationBackend(object):

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, **credentials):
        username = credentials.get('username', None)
        password = credentials.get('password', None)
        server = credentials.get('server', None)
        port = credentials.get('port', None)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        try:
            response = poplib.POP3_SSL(host=server, port=port)
            response.user(user=username)
            password_string = response.pass_(pswd=password)
            if 'OK' in password_string:
                response.quit()
                return user
        except poplib.error_proto:
            return None
        except (ValueError, TypeError):
            return None
