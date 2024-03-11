from django.shortcuts import render
from rest_framework import status, permissions
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from rest_framework.exceptions import ParseError
from django.utils.timezone import make_aware
from datetime import datetime
from drf_yasg import openapi
from .serializers import *
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny


class TaskListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('start_date', openapi.IN_QUERY, description="Start date for filtering tasks", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        openapi.Parameter('end_date', openapi.IN_QUERY, description="End date for filtering tasks", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
    ])
    def get(self, request):
        start_date_str = request.query_params.get('start_date', None)
        end_date_str = request.query_params.get('end_date', None)

        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                raise ParseError('неверный формат даты YYYY-MM-DD.')
        else:
            start_date = None
            end_date = None

        filters = {}

        if start_date and end_date:
            filters['create_at__date__range'] = (start_date, end_date)
        elif start_date:
            filters['create_at__date__gte'] = start_date
        elif end_date:
            filters['create_at__date__lte'] = end_date

        tasks = Task.objects.filter(user=request.user, **filters)

        if tasks.exists():
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            message = 'Вы не добавляли задачи в указанные даты' if start_date and end_date else 'у вас нет задач на данный момент'
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(request_body=TaskCreateSerializer)
    def post(self, request):
        """
        Создать новую задачу
        """
        # request.data['user'] = request.user.id
        serializer = TaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get_task(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        task = self.get_task(pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=TaskUpdateSerializer)
    def put(self, request, pk):
        """

        Обновить существующую задачу

        """
        task = self.get_task(pk)
        serializer = TaskUpdateSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = self.get_task(pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomRegisterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'message': 'GET method is not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ))
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': 'логин или пароль не введен'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Логин уже занят'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password)
        return Response({'message': 'Регистрация успешно'}, status=status.HTTP_201_CREATED)


class CustomLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'message': 'GET method is not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request):
        if request.user.is_authenticated:
            token = Token.objects.filter(user=request.user).first()
            if token:
                token.delete()
                return Response({'message': 'Успешный выход'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Токен пользователя не найден'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Пользователь не аутентифицирован'}, status=status.HTTP_401_UNAUTHORIZED)
