from rest_framework import authentication, exceptions
from django.conf import settings
from keycloak.keycloak_openid import KeycloakOpenID


def get_keycloak_open_id():
    return KeycloakOpenID(
        server_url=settings.KEYCLOAK_CONFIG["SERVER_URL"],
        realm_name=settings.KEYCLOAK_CONFIG["REALM_NAME"],
        client_secret_key=settings.KEYCLOAK_CONFIG["CLIENT_SECREAT"],
        client_id=settings.KEYCLOAK_CONFIG["CLIENT_ID"],
    )


class KeyCloakUser:
    def __init__(self, payload):
        self.id = payload.get("sub")
        self.username = payload.get("preferred_username")
        self.email = payload.get("email")
        self.is_authenticated = True
        self.is_active = True

    def __str__(self):
        return self.username or str(self.id)


class KeyCloakAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        token = parts[1]
        try:
            keycloak_open_id = get_keycloak_open_id()
            token_payload = keycloak_open_id.decode_token(token, validate=True)
        except Exception:
            raise exceptions.AuthenticationFailed("Invalid or expired token.")

        if not token_payload.get("sub"):
            raise exceptions.AuthenticationFailed("Invalid token payload.")

        return (KeyCloakUser(token_payload), token)
