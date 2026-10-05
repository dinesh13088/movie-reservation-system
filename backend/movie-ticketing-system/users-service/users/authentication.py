from  rest_framework import authentication

class KeyCloakAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        return super().authenticate(request)
