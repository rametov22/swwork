from django.urls import path
from .swagger import *
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt import authentication as jwt_authentication
from .views import *


class CustomTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(
        responses={200: openapi.Response("Token is successfully retrieved.")},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


urlpatterns = [
    path('tasks/', TaskListCreateAPIView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', TaskDetailAPIView.as_view(), name='task-detail'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('register/', CustomRegisterView.as_view(), name='api_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='api_token_auth'),
    path('logout/', CustomLogoutView.as_view(), name='api_logout'),
]
