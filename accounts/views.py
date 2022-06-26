from datetime import timedelta

import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import RegisterSerializer, LoginSerializer, JWTSerializer


class RegisterView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)

        return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)


class LoginView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    user = None
    access_token = None
    refresh_token = None
    access_token_expiration = timezone.now() + timedelta(hours=2)
    refresh_token_expiration = timezone.now() + timedelta(days=7)

    def generate_jwt_token(self):
        access_payload = {"pk": self.user.pk, "exp": self.access_token_expiration}
        refresh_payload = {"pk": self.user.pk, "exp": self.refresh_token_expiration}
        self.access_token = jwt.encode(
            access_payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        self.refresh_token = jwt.encode(
            refresh_payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

    def login(self):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        self.user = serializer.validated_data["user"]
        self.generate_jwt_token()

    def get_response(self):
        data = {
            "user": self.user,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "access_token_expiration": self.access_token_expiration,
            "refresh_token_expiration": self.refresh_token_expiration,
        }

        serializer = JWTSerializer(data, context=self.get_serializer_context())
        print(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        self.login()
        return self.get_response()

# class LoginView(GenericAPIView):
#     permission_classes = (AllowAny,)
#     serializer_class = LoginSerializer
#
#     school = None
#     access_token = None
#     access_token_expiration = timedelta(hours=2)
#     refresh_token = None
#     refresh_token_expiration = timedelta(days=7)
#
#     def generate_jwt_token(self, token):
#         if token == 'access':
#             token_expiration = timezone.now() + self.access_token_expiration
#         elif token == 'refresh':
#             token_expiration = timezone.now() + self.refresh_token_expiration
#         else:
#             raise Exception('Invalid Token Type')
#
#         payload = {"name": self.school.name, "exp": token_expiration}
#         token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
#         return token
#
#     def get_response(self):
#         data = {
#             "access_token": self.access_token,
#             "access_token_expiration": self.access_token_expiration.total_seconds(),
#         }
#         serializer = JWTSerializer(data, context=self.get_serializer_context())
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def login(self):
#         self.access_token = self.generate_jwt_token('access')
#         self.refresh_token = self.generate_jwt_token('refresh')
#         response = self.get_response()
#         response.set_cookie(
#             key='refresh_token',
#             value='test',
#             # value=self.refresh_token,
#             max_age=self.refresh_token_expiration.total_seconds(),
#             domain='localhost',
#             path='/',
#             samesite=None,
#             secure=True,
#             httponly=True)
#         return response
#
#     def post(self, request, *args, **kwargs):
#         self.request.data['ip'] = request.META["REMOTE_ADDR"]
#         serializer = self.get_serializer(data=self.request.data)
#         serializer.is_valid(raise_exception=True)
#         self.school = serializer.validated_data
#         return self.login()
#
#     def get(self, request, *args, **kwargs):
#         self.refresh_token = request.COOKIES.get('refresh_token', None)
#
#         if self.refresh_token is None:
#             return JsonResponse({'message': 'NO_REFRESH_TOKEN'}, status=401)
#
#         try:
#             payload = jwt.decode(self.refresh_token, settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
#             self.school = School.objects.get(name=payload['name'])
#             self.access_token = self.generate_jwt_token('access')
#             return self.get_response()
#
#         except jwt.ExpiredSignatureError or jwt.exceptions.DecodeError:
#             return JsonResponse({'message': 'NEED_LOGIN'}, status=401)
#
#         except School.DoesNotExist:
#             return JsonResponse({'message': 'INVALID_SCHOOL'}, status=401)


# class LogoutView(GenericAPIView):
#     @assert_login
#     def get(self, request):
#         response = Response(status=status.HTTP_202_ACCEPTED)
#         response.delete_cookie('refresh_token')
#         return response
#
#
# class SchoolDetail(APIView):
#     @assert_login
#     def get(self, request):
#         serializer = SchoolSerializer(request.user)
#         return Response(serializer.data, status=status.HTTP_200_OK)
