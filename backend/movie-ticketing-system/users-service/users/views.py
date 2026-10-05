from django.shortcuts import render
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.permissions import AllowAny

from keycloak.exceptions import KeycloakError,KeycloakPostError,KeycloakAuthenticationError
from keycloak.keycloak_admin import KeycloakAdmin
from keycloak.keycloak_openid import KeycloakOpenID


from .serializers import UserRegisterationSerializer,LoginSerializer
from .models import CustomUser
import logging

logger = logging.getLogger(__name__)
class UserRegisterationView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        
        serializer=UserRegisterationSerializer(data=request.data)
       
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        validated_data=serializer.validated_data
        print("VALIDATED:", dict(serializer.validated_data), flush=True)
        email=validated_data['email']
        password=validated_data["password"]
        fullname=validated_data["fullname"]
        username=validated_data["username"]
        firstname,lastname=fullname.split()

        try:
            with transaction.atomic():
                keycloak_admin=KeycloakAdmin(
                    server_url=settings.KEYCLOAK_CONFIG["SERVER_URL"],
                    realm_name=settings.KEYCLOAK_CONFIG["REALM_NAME"],
                    client_id=settings.KEYCLOAK_CONFIG["ADMIN_CLIENT_ID"],
                    client_secret_key=settings.KEYCLOAK_CONFIG["ADMIN_CLIENT_SECREAT"]

                )
                key_cloak_user_payload = {
                    "email": email,
                    "enabled": True,
                    "username": username,
                    "emailVerified": True,
                    "firstName": firstname,
                    "lastName": lastname,
                    "credentials": [
                        {
                            "type": "password",
                            "value": password,
                            "temporary": False,
                        }
                    ],
                }
                keycloak_id=keycloak_admin.create_user(payload=key_cloak_user_payload,exist_ok=False)
                user=CustomUser.objects.create_user(
                    email=email,
                    fullname=fullname,
                    username=username,
                    keycloak_id=keycloak_id
                )
                return Response({"message":"user registered successfully.Please login","fullname":user.fullname},status=status.HTTP_201_CREATED)

        except KeycloakPostError as e:

            error_msg=str(e)
            if "User exists with same username or email" in error_msg:
                return Response({
                    "error":"A user with this username or email already exists"
                },status=status.HTTP_409_CONFLICT)
            return Response({"error":f"keycloak registeration failed{error_msg}"},status=status.HTTP_400_BAD_REQUEST)
        except KeycloakError as e:
            return Response({"error":"authenticatin service is currently unavailable"},status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as e:
            return Response({"error":"an unexpected error occur"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_keycloak_open_id():
    return KeycloakOpenID(
        server_url=settings.KEYCLOAK_CONFIG["SERVER_URL"],
        realm_name=settings.KEYCLOAK_CONFIG["REALM_NAME"],
        client_secret_key=settings.KEYCLOAK_CONFIG["CLIENT_SECREAT"],
        client_id=settings.KEYCLOAK_CONFIG["CLIENT_ID"]
    )

class LoginView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "error":"this is not validated data"
            })
        data=serializer.validated_data
        username=data["username"]
        password=data["password"]
        try:
            keycloak_open_id = get_keycloak_open_id()
            tokens = keycloak_open_id.token(username=username, password=password)
            access_token = tokens["access_token"]
            refresh_token = tokens["refresh_token"]

            token_payload = keycloak_open_id.decode_token(access_token, validate=True)

            keycloak_id = token_payload.get("sub")
            kc_username = token_payload.get("preferred_username")
            email = token_payload.get("email", "")

            user, created = CustomUser.objects.get_or_create(
                keycloak_id=keycloak_id,
                defaults={"username": kc_username, "email": email},
            )

            if not created:
                if user.email != email or user.username != kc_username:
                    user.email = email
                    user.username = kc_username
                    user.save()

            return Response({
                "message": "logged in successfully",
                "accessToken": access_token,
                "refreshToken": refresh_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            }, status=status.HTTP_200_OK)

        except KeycloakAuthenticationError:
            return Response({"error": "invalid username and password"},
                            status=status.HTTP_401_UNAUTHORIZED)
        except KeycloakError as e:
            try:
                detail = e.response.json()
            except Exception:
                detail = str(e)
            logger.warning("Keycloak token error: %s", detail)
            return Response({"error": "authentication service error", "detail": detail},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception:
            logger.exception("Unexpected error during login")
            return Response({"error": "unexpected error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TokenRefreshView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        refresh_token=request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            keycloak_openid=get_keycloak_open_id()
            tokens=keycloak_openid.refresh_token(refresh_token=refresh_token)
            return Response({
                "accessToken":tokens["access_token"],
                "refreshToken":tokens.get("refresh_token")
            },status=status.HTTP_200_OK)
        except KeycloakError:
            return Response(
                {"error": "Invalid or expired refresh token. Please log in again."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )










    




        

