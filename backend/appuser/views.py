from rest_framework import generics, permissions, status
from rest_framework.response import Response
from knox.models import AuthToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from jwt import encode, decode, ExpiredSignatureError, exceptions

from .models import CustomUser as User
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from .utils import Util


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

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })
