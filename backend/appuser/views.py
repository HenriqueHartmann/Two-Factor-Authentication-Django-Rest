from rest_framework import generics, permissions, status
from rest_framework.response import Response
from knox.models import AuthToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from jwt import encode, decode, ExpiredSignatureError, exceptions
from datetime import datetime, timedelta

from .models import CustomUser as User, LoginAdmin
from .serializers import UserSerializer, RegisterSerializer,\
    LoginSerializer, UpdateLoginAdminSerializer, CreateLoginAdminSerializer, PinValidationSerializer
from .utils import Util

# Constants
date_format = "%d-%m-%YT%H:%M:%S"


# Functions
def deactivate_all_loginadmins(user_id):
    if LoginAdmin.objects.count() > 0:
        datas = LoginAdmin.objects.all()
        for loginadmin in datas:
            if loginadmin.user_id == user_id:
                serializer = UpdateLoginAdminSerializer(loginadmin, data={'active': False})
                serializer.is_valid(raise_exception=True)
                serializer.save()


def create_login_admin(user_id):
    date_now = datetime.now()
    request = {
        'user': user_id,
        'created_at': date_now.strftime(date_format),
        'valid_until': (date_now + timedelta(minutes=20)).strftime(date_format)
    }
    serializer = CreateLoginAdminSerializer(data=request)
    serializer.is_valid(raise_exception=True)
    serializer.save()


def get_login(user_id):
    data = LoginAdmin.objects.all().filter(user_id=user_id, active=True)
    return data[0]


# Views
class UserAPIView(generics.RetrieveAPIView):

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        return self.request.user


class RegisterAPIView(generics.GenericAPIView):

    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        user_data = User.objects.get(email=serializer.data['email'])
        token = encode({'id': user_data.id}, settings.SECRET_KEY, algorithm='HS256')
        current_site = get_current_site(request).domain
        relative_link = reverse('email-verify')
        absurl = 'http://' + current_site + relative_link + "?token=" + str(token)

        email_body = 'Hi ' + user_data.fullname + ' User the link bellow to verify your email: \n' + absurl
        data = {'to_email': user_data.email, 'email_subject': 'Verify your email', 'email_body': email_body}
        Util.send_email(data)

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data
        }, status=status.HTTP_201_CREATED)


class VerifyEmail(generics.GenericAPIView):

    @staticmethod
    def get(request):
        token = request.GET.get('token')
        try:
            payload = decode(token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(id=payload['id'])
            if user.email_validation is False:
                user.email_validation = True
                user.save()
            return Response({'message': 'Successfully activated'}, status=status.HTTP_200_OK)
        except ExpiredSignatureError:
            return Response({'message': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except exceptions.DecodeError:
            return Response({'message': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):

    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny, ]

    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        if user.email_validation is False:
            return Response({
                "message": "Seu usuário não foi ativado"
            }, status=status.HTTP_400_BAD_REQUEST)

        if user.profile == 'admin':
            deactivate_all_loginadmins(user.id)
            create_login_admin(user.id)
            login = get_login(user.id)
            pin = login.pin
            token = encode({'id': user.id, 'login_id': login.id, 'pin': pin, 'expired': login.valid_until},
                           settings.SECRET_KEY, algorithm='HS256')
            current_site = get_current_site(request).domain
            relative_link = reverse('admin-verify')
            absurl = 'http://' + current_site + relative_link + "?token=" + str(token)
            email_body = 'Hi ' + user.fullname + '. You are trying to login with an admin account, ' \
                                                 'so we need a confirmation.' \
                                                 'Use this code: ' + pin
            data = {'to_email': user.email, 'email_subject': 'Validate your login', 'email_body': email_body}
            Util.send_email(data)

            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "link": absurl
            })
        else:
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": AuthToken.objects.create(user)[1]
            })


class VerifyAdmin(generics.GenericAPIView):

    serializer_class = PinValidationSerializer
    permission_classes = [permissions.AllowAny, ]

    @staticmethod
    def get(request):
        serializer = PinValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = request.GET.get('token')
        try:
            payload = decode(token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.filter(id=payload['id'])[0]
            login_id = payload['login_id']
            pin = payload['pin']
            expired = datetime.strptime(payload['expired'], date_format)
            date_now = datetime.now()
            if date_now <= expired:
                if pin == serializer.validated_data['pin']:
                    login_obj = LoginAdmin.objects.filter(id=login_id)[0]
                    login_obj.validated = True
                    login_obj.save()
                    serializer = UserSerializer(user)
                    return Response({
                        "message": "Successfully validated",
                        "user": serializer.data,
                        "token": AuthToken.objects.create(user)[1]
                        },
                        status=status.HTTP_200_OK)
                else:
                    return Response({"message": "The pin that you trying to insert not matched our records"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Token Expired"}, status=status.HTTP_400_BAD_REQUEST)
        except ExpiredSignatureError:
            return Response({'message': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except exceptions.DecodeError:
            return Response({'message': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)
